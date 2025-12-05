"""
Fiido 电商网站产品爬虫模块

负责从 Fiido.com 网站发现和抓取商品信息，支持 Shopify JSON API 和 HTML 解析两种方式。
集成缓存机制，提升性能。
"""

import logging
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from core.models import Product, ProductVariant, Selectors
from core.cache import CrawlerCache

logger = logging.getLogger(__name__)


class ProductCrawler:
    """Fiido 网站产品爬虫

    实现商品分类发现、商品列表抓取、商品详情解析等功能。
    优先使用 Shopify JSON API，失败时降级到 HTML 解析。
    支持缓存机制，避免重复爬取。
    """

    def __init__(
        self,
        base_url: str = "https://fiido.com",
        timeout: int = 30,
        max_retries: int = 3,
        use_cache: bool = True,
        cache_ttl_hours: int = 24
    ):
        """初始化产品爬虫

        Args:
            base_url: 网站根 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            use_cache: 是否启用缓存
            cache_ttl_hours: 缓存有效期（小时）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.use_cache = use_cache

        # 初始化缓存
        if use_cache:
            self.cache = CrawlerCache(ttl_hours=cache_ttl_hours)
            print(f"✅ 缓存已启用（TTL: {cache_ttl_hours}小时）")
        else:
            self.cache = None

        # 配置带重试机制的 Session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })

        logger.info(f"ProductCrawler initialized for {base_url}")

    def discover_collections(self) -> List[str]:
        """发现所有商品分类

        优先从官网主页发现分类，失败时尝试 /collections 页面。
        会自动去除重复分类。

        Returns:
            分类 URL 列表，例如：['/collections/bikes', '/collections/accessories']

        Raises:
            requests.RequestException: 网络请求失败
        """
        collection_links = set()

        # 策略1: 从主页发现分类（优先）
        try:
            logger.info(f"Discovering collections from homepage: {self.base_url}")
            homepage_collections = self._discover_collections_from_page(self.base_url)
            collection_links.update(homepage_collections)
            logger.info(f"Found {len(homepage_collections)} collections from homepage")
        except Exception as e:
            logger.warning(f"Failed to discover from homepage: {e}")

        # 策略2: 从 /collections 页面发现（补充）
        try:
            collections_url = f"{self.base_url}/collections"
            logger.info(f"Discovering collections from: {collections_url}")
            collections_page = self._discover_collections_from_page(collections_url)
            collection_links.update(collections_page)
            logger.info(f"Found {len(collections_page)} collections from /collections page")
        except Exception as e:
            logger.warning(f"Failed to discover from /collections page: {e}")

        if not collection_links:
            logger.error("No collections found! Please check the website structure.")
            raise ValueError("No collections found")

        result = sorted(list(collection_links))
        logger.info(f"📊 Total unique collections discovered: {len(result)}")
        logger.info(f"Collections: {result}")
        return result

    def _discover_collections_from_page(self, url: str) -> set:
        """从指定页面发现商品分类链接

        Args:
            url: 要扫描的页面URL

        Returns:
            分类URL集合
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        collection_links = set()

        # 策略1: 查找包含 /collections/ 的所有链接
        for link in soup.find_all('a', href=True):
            href = link['href']
            if '/collections/' in href and href != '/collections' and href != '/collections/':
                # 标准化 URL
                if href.startswith('http'):
                    # 绝对 URL，提取路径部分
                    if self.base_url in href:
                        href = href.split(self.base_url)[1]
                    else:
                        continue
                elif not href.startswith('/'):
                    # 相对路径，添加前导斜杠
                    href = '/' + href

                # 移除查询参数和锚点
                href = href.split('?')[0].split('#')[0]

                # 过滤掉无效的路径
                if self._is_valid_collection_path(href):
                    collection_links.add(href)

        # 策略2: 查找导航菜单中的分类链接（Shopify 常见模式）
        nav_selectors = [
            '.site-nav a[href*="/collections/"]',
            '.menu a[href*="/collections/"]',
            '.navigation a[href*="/collections/"]',
            'nav a[href*="/collections/"]',
            'header a[href*="/collections/"]',
            '.header a[href*="/collections/"]'
        ]

        for selector in nav_selectors:
            for link in soup.select(selector):
                href = link.get('href', '')
                if href and '/collections/' in href:
                    href = href.split('?')[0].split('#')[0]
                    if not href.startswith('http') and self._is_valid_collection_path(href):
                        collection_links.add(href)

        return collection_links

    def _is_valid_collection_path(self, path: str) -> bool:
        """检查是否为有效的分类路径

        Args:
            path: URL路径

        Returns:
            是否有效
        """
        # 排除一些已知的非分类路径
        invalid_patterns = [
            '/collections/all',
            '/collections/vendors',
            '/collections/types',
            '/account',
            '/cart',
            '/checkout',
            '/search',
            '/pages/'
        ]

        for pattern in invalid_patterns:
            if pattern in path:
                return False

        # 必须以 /collections/ 开头且后面有内容
        if not path.startswith('/collections/'):
            return False

        # 提取分类名称部分
        collection_name = path.replace('/collections/', '')
        if not collection_name or collection_name == '':
            return False

        return True

    def _format_category_name(self, category_slug: str) -> str:
        """格式化分类名称，将URL slug转换为友好的显示名称

        Args:
            category_slug: URL中的分类名称，如 'electric-bikes'

        Returns:
            格式化后的分类名称，如 'Electric Bikes'
        """
        # 替换连字符为空格
        category = category_slug.replace('-', ' ').replace('_', ' ')

        # 首字母大写（Title Case）
        category = category.title()

        # 处理一些特殊的缩写词，保持大写
        special_words = {
            'Ebike': 'eBike',
            'Ebikes': 'eBikes',
            'E Bike': 'E-Bike',
            'E Bikes': 'E-Bikes'
        }

        for old, new in special_words.items():
            category = category.replace(old, new)

        return category

    def discover_products(
        self,
        collection_path: str,
        limit: Optional[int] = None
    ) -> List[Product]:
        """从指定分类中发现所有商品

        优先使用 Shopify JSON API（.json 后缀），失败时降级到 HTML 解析。

        Args:
            collection_path: 分类路径，例如 '/collections/bikes'
            limit: 限制抓取商品数量，None 表示不限制

        Returns:
            Product 对象列表

        Raises:
            requests.RequestException: 网络请求失败
        """
        logger.info(f"Discovering products from {collection_path} (limit: {limit})")

        # 优先尝试 Shopify JSON API
        try:
            products = self._discover_products_via_json(collection_path, limit)
            if products:
                logger.info(f"Discovered {len(products)} products via JSON API")
                return products
        except Exception as e:
            logger.warning(f"JSON API failed, falling back to HTML parsing: {e}")

        # 降级到 HTML 解析
        try:
            products = self._discover_products_via_html(collection_path, limit)
            logger.info(f"Discovered {len(products)} products via HTML parsing")
            return products
        except Exception as e:
            logger.error(f"Failed to discover products: {e}")
            raise

    def _discover_products_via_json(
        self,
        collection_path: str,
        limit: Optional[int] = None
    ) -> List[Product]:
        """通过 Shopify JSON API 发现商品

        Args:
            collection_path: 分类路径，例如 '/collections/electric-bikes'
            limit: 限制抓取商品数量

        Returns:
            Product 对象列表
        """
        # 构建正确的 Shopify JSON API URL
        # 格式: /collections/{handle}/products.json (不是 /collections/{handle}.json)
        json_url = f"{self.base_url}{collection_path}/products.json"
        products = []
        page = 1

        while True:
            # Shopify JSON API 分页参数
            params = {'page': page, 'limit': 250}  # Shopify 最多支持每页250个商品
            if limit and len(products) >= limit:
                break

            logger.debug(f"Fetching {json_url}?page={page}")
            response = self.session.get(json_url, params=params, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()

            # Shopify 返回格式: {"products": [...]}
            if 'products' not in data or not data['products']:
                break

            for product_data in data['products']:
                if limit and len(products) >= limit:
                    break

                product = self._parse_product_from_json(product_data, collection_path)
                if product:
                    products.append(product)

            # 如果返回商品数量少于请求的limit，说明已到最后一页
            if len(data['products']) < 250:
                break

            page += 1
            time.sleep(0.5)  # 避免请求过快

        return products

    def _parse_product_from_json(
        self,
        product_data: Dict[str, Any],
        collection_path: str
    ) -> Optional[Product]:
        """从 Shopify JSON 数据解析商品信息

        Args:
            product_data: Shopify 产品 JSON 数据
            collection_path: 所属分类路径

        Returns:
            Product 对象，解析失败返回 None
        """
        try:
            # 构建商品 URL
            handle = product_data.get('handle', '')
            product_url = f"{self.base_url}/products/{handle}"

            # 检查缓存
            if self.use_cache and self.cache:
                cached_data = self.cache.get(product_url)
                if cached_data:
                    try:
                        return Product(**cached_data)
                    except Exception as e:
                        logger.warning(f"Failed to load from cache: {e}")

            # 提取基本信息
            product_id = str(product_data.get('id', ''))

            # 提取价格范围
            variants_data = product_data.get('variants', [])
            prices = [float(v.get('price', 0)) for v in variants_data if v.get('price')]

            if not prices:
                logger.warning(f"Product {handle} has no valid prices, skipping")
                return None

            price_min = min(prices)
            price_max = max(prices)

            # 提取变体信息
            variants = []
            for variant_data in variants_data:
                variant = self._parse_variant_from_json(variant_data)
                if variant:
                    variants.append(variant)

            # 提取分类名称 - 保留原始官网分类
            # 从 collection_path 提取，例如 '/collections/electric-bikes' -> 'Electric Bikes'
            category_slug = collection_path.split('/')[-1]
            category = self._format_category_name(category_slug)

            # 提取标签
            tags = product_data.get('tags', [])
            if isinstance(tags, str):
                tags = [t.strip() for t in tags.split(',')]

            # 创建默认选择器（将在运行时由 SelectorManager 更新）
            selectors = Selectors()

            product = Product(
                id=product_id,
                name=product_data.get('title', ''),
                url=product_url,
                category=category,
                price_min=price_min,
                price_max=price_max,
                currency="USD",
                variants=variants,
                selectors=selectors,
                priority="P1",
                tags=tags,
                metadata={
                    'vendor': product_data.get('vendor', ''),
                    'product_type': product_data.get('product_type', ''),
                    'handle': handle,
                    'available': product_data.get('available', False),
                    'collection_path': collection_path,  # 保留原始分类路径
                    'category_slug': category_slug  # 保留URL友好的分类名称
                }
            )

            # 保存到缓存
            if self.use_cache and self.cache:
                self.cache.set(product_url, product.model_dump(mode='json'))

            return product

        except Exception as e:
            logger.error(f"Failed to parse product from JSON: {e}")
            return None

    def _parse_variant_from_json(
        self,
        variant_data: Dict[str, Any]
    ) -> Optional[ProductVariant]:
        """从 Shopify JSON 数据解析商品变体

        Args:
            variant_data: Shopify 变体 JSON 数据

        Returns:
            ProductVariant 对象，解析失败返回 None
        """
        try:
            # Shopify 变体结构: option1, option2, option3
            options = []
            for i in range(1, 4):
                option = variant_data.get(f'option{i}')
                if option and option.lower() not in ['default title', 'default']:
                    options.append(option)

            if not options:
                return None

            # 推断变体类型
            variant_name = ' / '.join(options)
            variant_type = self._infer_variant_type(variant_name)

            # 生成选择器（将在运行时动态调整）
            selector = f"[data-variant-id='{variant_data.get('id')}']"

            return ProductVariant(
                name=variant_name,
                type=variant_type,
                selector=selector,
                available=variant_data.get('available', False),
                price_modifier=None  # 价格差异在 Product 中已体现
            )

        except Exception as e:
            logger.error(f"Failed to parse variant from JSON: {e}")
            return None

    def _infer_variant_type(self, variant_name: str) -> str:
        """推断变体类型

        Args:
            variant_name: 变体名称，如 'Black', 'Large', 'Sport'

        Returns:
            变体类型: 'color', 'size', 'style', 'configuration'
        """
        name_lower = variant_name.lower()

        # 颜色关键词
        color_keywords = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'gray', 'silver']
        if any(keyword in name_lower for keyword in color_keywords):
            return 'color'

        # 尺寸关键词
        size_keywords = ['small', 'medium', 'large', 'xs', 's', 'm', 'l', 'xl', 'xxl']
        if any(keyword == name_lower or keyword in name_lower.split() for keyword in size_keywords):
            return 'size'

        # 配置关键词
        config_keywords = ['standard', 'pro', 'plus', 'premium', 'basic', 'advanced']
        if any(keyword in name_lower for keyword in config_keywords):
            return 'configuration'

        # 默认为样式
        return 'style'

    def _discover_products_via_html(
        self,
        collection_path: str,
        limit: Optional[int] = None
    ) -> List[Product]:
        """通过 HTML 解析发现商品（降级方案）

        Args:
            collection_path: 分类路径
            limit: 限制抓取商品数量

        Returns:
            Product 对象列表
        """
        collection_url = f"{self.base_url}{collection_path}"
        response = self.session.get(collection_url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        products = []

        # 查找商品链接（Shopify 常见模式）
        product_selectors = [
            '.product-item a[href*="/products/"]',
            '.product-card a[href*="/products/"]',
            '.grid-item a[href*="/products/"]',
            'a.product-link[href*="/products/"]',
            'a[href*="/products/"]'
        ]

        product_links = set()
        for selector in product_selectors:
            for link in soup.select(selector):
                href = link.get('href', '')
                if '/products/' in href:
                    # 标准化 URL
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)

                    # 移除查询参数
                    href = href.split('?')[0]
                    product_links.add(href)

                    if limit and len(product_links) >= limit:
                        break

            if limit and len(product_links) >= limit:
                break

        # 提取分类名称
        category = collection_path.split('/')[-1].replace('-', ' ').title()

        # 为每个商品链接创建基本 Product 对象
        for product_url in sorted(product_links):
            if limit and len(products) >= limit:
                break

            # 从 URL 提取 handle
            handle = product_url.split('/products/')[-1].split('?')[0]

            # 创建基本商品对象（详细信息需要进一步抓取）
            product = Product(
                id=handle,
                name=handle.replace('-', ' ').title(),
                url=product_url,
                category=category,
                price_min=0.0,  # 需要进一步抓取
                price_max=0.0,
                currency="USD",
                variants=[],
                selectors=Selectors(),
                priority="P1",
                tags=[],
                metadata={'handle': handle, 'needs_detail_fetch': True}
            )

            products.append(product)

        logger.info(f"Found {len(products)} product links via HTML parsing")
        return products

    def close(self):
        """关闭 Session，释放资源"""
        self.session.close()
        logger.info("ProductCrawler session closed")
