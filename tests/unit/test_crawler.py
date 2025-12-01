"""
ProductCrawler 单元测试

测试商品爬虫的各项功能，包括分类发现、商品抓取、JSON解析、HTML解析等。
"""

import json
from unittest.mock import Mock, patch, MagicMock
import pytest
import requests

from core.crawler import ProductCrawler
from core.models import Product, ProductVariant, Selectors


class TestProductCrawlerInit:
    """测试 ProductCrawler 初始化"""

    def test_init_with_defaults(self):
        """测试使用默认参数初始化"""
        crawler = ProductCrawler()
        assert crawler.base_url == "https://fiido.com"
        assert crawler.timeout == 30
        assert crawler.session is not None
        assert 'User-Agent' in crawler.session.headers

    def test_init_with_custom_params(self):
        """测试使用自定义参数初始化"""
        crawler = ProductCrawler(
            base_url="https://example.com",
            timeout=60,
            max_retries=5
        )
        assert crawler.base_url == "https://example.com"
        assert crawler.timeout == 60

    def test_init_strips_trailing_slash(self):
        """测试初始化时移除 URL 尾部斜杠"""
        crawler = ProductCrawler(base_url="https://fiido.com/")
        assert crawler.base_url == "https://fiido.com"


class TestDiscoverCollections:
    """测试分类发现功能"""

    @patch('core.crawler.requests.Session.get')
    def test_discover_collections_success(self, mock_get):
        """测试成功发现分类"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <nav>
                <a href="/collections/bikes">Bikes</a>
                <a href="/collections/accessories">Accessories</a>
                <a href="/collections/spare-parts">Spare Parts</a>
                <a href="/about">About</a>
            </nav>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        collections = crawler.discover_collections()

        assert len(collections) == 3
        assert '/collections/bikes' in collections
        assert '/collections/accessories' in collections
        assert '/collections/spare-parts' in collections
        assert '/about' not in collections

    @patch('core.crawler.requests.Session.get')
    def test_discover_collections_with_query_params(self, mock_get):
        """测试处理带查询参数的分类链接"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <a href="/collections/bikes?sort=price">Bikes</a>
            <a href="/collections/bikes#featured">Bikes Featured</a>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        collections = crawler.discover_collections()

        # 应该去除查询参数和锚点，只保留一个
        assert collections == ['/collections/bikes']

    @patch('core.crawler.requests.Session.get')
    def test_discover_collections_network_error(self, mock_get):
        """测试网络错误处理"""
        mock_get.side_effect = requests.RequestException("Network error")

        crawler = ProductCrawler()
        with pytest.raises(requests.RequestException):
            crawler.discover_collections()

    @patch('core.crawler.requests.Session.get')
    def test_discover_collections_empty_page(self, mock_get):
        """测试空页面处理"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body><p>No collections</p></body></html>"
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        collections = crawler.discover_collections()

        assert collections == []


class TestDiscoverProducts:
    """测试商品发现功能"""

    @patch('core.crawler.ProductCrawler._discover_products_via_json')
    def test_discover_products_via_json_success(self, mock_json):
        """测试通过 JSON API 成功发现商品"""
        mock_products = [
            Product(
                id="1",
                name="Test Bike",
                url="https://fiido.com/products/test-bike",
                category="Bikes",
                price_min=100.0,
                price_max=100.0,
                currency="USD",
                variants=[],
                selectors=Selectors()
            )
        ]
        mock_json.return_value = mock_products

        crawler = ProductCrawler()
        products = crawler.discover_products('/collections/bikes')

        assert len(products) == 1
        assert products[0].name == "Test Bike"
        mock_json.assert_called_once()

    @patch('core.crawler.ProductCrawler._discover_products_via_json')
    @patch('core.crawler.ProductCrawler._discover_products_via_html')
    def test_discover_products_fallback_to_html(self, mock_html, mock_json):
        """测试 JSON 失败时降级到 HTML 解析"""
        mock_json.side_effect = Exception("JSON API failed")
        mock_html.return_value = [
            Product(
                id="2",
                name="Test Bike",
                url="https://fiido.com/products/test-bike",
                category="Bikes",
                price_min=0.0,
                price_max=0.0,
                currency="USD",
                variants=[],
                selectors=Selectors()
            )
        ]

        crawler = ProductCrawler()
        products = crawler.discover_products('/collections/bikes')

        assert len(products) == 1
        mock_json.assert_called_once()
        mock_html.assert_called_once()

    @patch('core.crawler.ProductCrawler._discover_products_via_json')
    def test_discover_products_with_limit(self, mock_json):
        """测试限制商品数量"""
        crawler = ProductCrawler()
        crawler.discover_products('/collections/bikes', limit=10)

        mock_json.assert_called_once_with('/collections/bikes', 10)


class TestDiscoverProductsViaJSON:
    """测试 JSON API 商品发现"""

    @patch('core.crawler.requests.Session.get')
    def test_discover_products_via_json_single_page(self, mock_get):
        """测试单页商品抓取"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'products': [
                {
                    'id': 123,
                    'title': 'Test Bike',
                    'handle': 'test-bike',
                    'variants': [
                        {
                            'id': 456,
                            'price': '999.00',
                            'available': True,
                            'option1': 'Black',
                            'option2': None,
                            'option3': None
                        }
                    ],
                    'tags': 'electric, bike',
                    'vendor': 'Fiido',
                    'product_type': 'Electric Bike',
                    'available': True
                }
            ]
        }
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        products = crawler._discover_products_via_json('/collections/bikes')

        assert len(products) == 1
        assert products[0].id == '123'
        assert products[0].name == 'Test Bike'
        assert products[0].price_min == 999.0
        assert len(products[0].variants) == 1

    @patch('core.crawler.requests.Session.get')
    def test_discover_products_via_json_multiple_pages(self, mock_get):
        """测试多页商品抓取"""
        # 第一页返回 30 个商品（触发翻页）
        page1_response = Mock()
        page1_response.status_code = 200
        page1_response.json.return_value = {
            'products': [
                {
                    'id': i,
                    'title': f'Product {i}',
                    'handle': f'product-{i}',
                    'variants': [{'id': i * 10, 'price': '100.00', 'available': True}],
                    'tags': [],
                    'vendor': 'Test',
                    'product_type': 'Test',
                    'available': True
                }
                for i in range(30)
            ]
        }

        # 第二页返回 5 个商品（结束翻页）
        page2_response = Mock()
        page2_response.status_code = 200
        page2_response.json.return_value = {
            'products': [
                {
                    'id': i,
                    'title': f'Product {i}',
                    'handle': f'product-{i}',
                    'variants': [{'id': i * 10, 'price': '100.00', 'available': True}],
                    'tags': [],
                    'vendor': 'Test',
                    'product_type': 'Test',
                    'available': True
                }
                for i in range(30, 35)
            ]
        }

        mock_get.side_effect = [page1_response, page2_response]

        crawler = ProductCrawler()
        products = crawler._discover_products_via_json('/collections/bikes')

        assert len(products) == 35
        assert mock_get.call_count == 2


class TestParseProductFromJSON:
    """测试 JSON 商品解析"""

    def test_parse_product_from_json_complete(self):
        """测试解析完整的商品数据"""
        product_data = {
            'id': 123456,
            'title': 'Fiido D11 Electric Bike',
            'handle': 'fiido-d11',
            'variants': [
                {
                    'id': 789,
                    'price': '999.00',
                    'available': True,
                    'option1': 'Black',
                    'option2': None,
                    'option3': None
                },
                {
                    'id': 790,
                    'price': '1099.00',
                    'available': True,
                    'option1': 'White',
                    'option2': None,
                    'option3': None
                }
            ],
            'tags': 'electric, folding, bike',
            'vendor': 'Fiido',
            'product_type': 'Electric Bike',
            'available': True
        }

        crawler = ProductCrawler()
        product = crawler._parse_product_from_json(product_data, '/collections/bikes')

        assert product is not None
        assert product.id == '123456'
        assert product.name == 'Fiido D11 Electric Bike'
        assert str(product.url) == 'https://fiido.com/products/fiido-d11'
        assert product.price_min == 999.0
        assert product.price_max == 1099.0
        assert product.category == 'Bikes'
        assert len(product.variants) == 2
        assert len(product.tags) == 3

    def test_parse_product_from_json_no_price(self):
        """测试解析无价格商品（应跳过）"""
        product_data = {
            'id': 123,
            'title': 'Test Product',
            'handle': 'test',
            'variants': [],
            'tags': '',
            'vendor': 'Test',
            'product_type': 'Test',
            'available': False
        }

        crawler = ProductCrawler()
        product = crawler._parse_product_from_json(product_data, '/collections/test')

        assert product is None

    def test_parse_product_from_json_invalid_data(self):
        """测试解析无效数据"""
        product_data = {'invalid': 'data'}

        crawler = ProductCrawler()
        product = crawler._parse_product_from_json(product_data, '/collections/test')

        assert product is None


class TestParseVariantFromJSON:
    """测试 JSON 变体解析"""

    def test_parse_variant_color(self):
        """测试解析颜色变体"""
        variant_data = {
            'id': 123,
            'option1': 'Black',
            'option2': None,
            'option3': None,
            'available': True,
            'price': '100.00'
        }

        crawler = ProductCrawler()
        variant = crawler._parse_variant_from_json(variant_data)

        assert variant is not None
        assert variant.name == 'Black'
        assert variant.type == 'color'
        assert variant.available is True

    def test_parse_variant_size(self):
        """测试解析尺寸变体"""
        variant_data = {
            'id': 124,
            'option1': 'Large',
            'option2': None,
            'option3': None,
            'available': True,
            'price': '100.00'
        }

        crawler = ProductCrawler()
        variant = crawler._parse_variant_from_json(variant_data)

        assert variant is not None
        assert variant.name == 'Large'
        assert variant.type == 'size'

    def test_parse_variant_multiple_options(self):
        """测试解析多选项变体"""
        variant_data = {
            'id': 125,
            'option1': 'Black',
            'option2': 'Large',
            'option3': 'Premium',
            'available': False,
            'price': '150.00'
        }

        crawler = ProductCrawler()
        variant = crawler._parse_variant_from_json(variant_data)

        assert variant is not None
        assert variant.name == 'Black / Large / Premium'
        assert variant.available is False

    def test_parse_variant_default_title(self):
        """测试解析默认标题（无变体）"""
        variant_data = {
            'id': 126,
            'option1': 'Default Title',
            'option2': None,
            'option3': None,
            'available': True,
            'price': '100.00'
        }

        crawler = ProductCrawler()
        variant = crawler._parse_variant_from_json(variant_data)

        assert variant is None


class TestInferVariantType:
    """测试变体类型推断"""

    def test_infer_color_type(self):
        """测试推断颜色类型"""
        crawler = ProductCrawler()
        assert crawler._infer_variant_type('Black') == 'color'
        assert crawler._infer_variant_type('White') == 'color'
        assert crawler._infer_variant_type('Deep Blue') == 'color'

    def test_infer_size_type(self):
        """测试推断尺寸类型"""
        crawler = ProductCrawler()
        assert crawler._infer_variant_type('Small') == 'size'
        assert crawler._infer_variant_type('L') == 'size'
        assert crawler._infer_variant_type('XL') == 'size'

    def test_infer_configuration_type(self):
        """测试推断配置类型"""
        crawler = ProductCrawler()
        assert crawler._infer_variant_type('Standard') == 'configuration'
        assert crawler._infer_variant_type('Pro') == 'configuration'
        assert crawler._infer_variant_type('Premium Edition') == 'configuration'

    def test_infer_style_type(self):
        """测试推断样式类型（默认）"""
        crawler = ProductCrawler()
        assert crawler._infer_variant_type('Sport') == 'style'
        assert crawler._infer_variant_type('Classic') == 'style'
        assert crawler._infer_variant_type('Unknown Option') == 'style'


class TestDiscoverProductsViaHTML:
    """测试 HTML 解析商品发现"""

    @patch('core.crawler.requests.Session.get')
    def test_discover_products_via_html_success(self, mock_get):
        """测试通过 HTML 成功发现商品"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <div class="product-grid">
                <div class="product-item">
                    <a href="/products/bike-1">Bike 1</a>
                </div>
                <div class="product-item">
                    <a href="/products/bike-2">Bike 2</a>
                </div>
            </div>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        products = crawler._discover_products_via_html('/collections/bikes')

        assert len(products) == 2
        assert products[0].id == 'bike-1'
        assert products[1].id == 'bike-2'
        assert products[0].category == 'Bikes'

    @patch('core.crawler.requests.Session.get')
    def test_discover_products_via_html_with_limit(self, mock_get):
        """测试 HTML 解析时限制商品数量"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <a href="/products/bike-1">Bike 1</a>
            <a href="/products/bike-2">Bike 2</a>
            <a href="/products/bike-3">Bike 3</a>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        products = crawler._discover_products_via_html('/collections/bikes', limit=2)

        assert len(products) == 2

    @patch('core.crawler.requests.Session.get')
    def test_discover_products_via_html_deduplication(self, mock_get):
        """测试 HTML 解析时去重"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <a href="/products/bike-1">Bike 1</a>
            <a href="/products/bike-1">Bike 1 Duplicate</a>
            <a href="/products/bike-1?variant=123">Bike 1 Variant</a>
        </html>
        """
        mock_get.return_value = mock_response

        crawler = ProductCrawler()
        products = crawler._discover_products_via_html('/collections/bikes')

        assert len(products) == 1


class TestCrawlerClose:
    """测试爬虫资源释放"""

    def test_close_session(self):
        """测试关闭 Session"""
        crawler = ProductCrawler()
        crawler.close()
        # Session 关闭后应该无法使用
        # 这里只是确保 close() 方法可以正常调用，不抛出异常
