#!/usr/bin/env python3
"""
HTML Website Test Suite
全てのテストを実行してコミット前の品質をチェック
"""

import os
import re
import sys
from html.parser import HTMLParser


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def run_test(self, name, func):
        """テストを実行"""
        print(f"\n{'='*60}")
        print(f"Test: {name}")
        print('='*60)
        try:
            func()
            print(f"✅ PASSED")
            self.passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            self.failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            self.failed += 1

    def summary(self):
        """テスト結果サマリー"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print('='*60)
        total = self.passed + self.failed
        print(f"Total: {total} tests")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")

        if self.failed == 0:
            print("\n🎉 All tests passed!")
            return 0
        else:
            print(f"\n💥 {self.failed} test(s) failed")
            return 1


def test_file_exists():
    """index.htmlファイルが存在するか"""
    assert os.path.exists('index.html'), "index.html not found"
    print("✓ index.html exists")


def test_all_images_exist():
    """全ての画像ファイルが存在するか"""
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = r'src=\"([^\"]+)\"'
    matches = re.findall(pattern, html)

    local_files = [m for m in matches if not m.startswith('http')]

    for src in local_files:
        assert os.path.exists(src), f"Image not found: {src}"
        print(f"✓ Found: {src}")

    print(f"\n✓ All {len(local_files)} local files exist")


def test_all_images_have_alt():
    """全ての画像にalt属性があるか"""
    class ImageChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.images = []
            self.errors = []

        def handle_starttag(self, tag, attrs):
            if tag == 'img':
                attrs_dict = dict(attrs)
                src = attrs_dict.get('src', '')
                alt = attrs_dict.get('alt', '')

                if not alt:
                    self.errors.append(f'Missing alt: {src}')
                else:
                    self.images.append({'src': src, 'alt': alt})

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    checker = ImageChecker()
    checker.feed(html)

    assert len(checker.errors) == 0, f"Images without alt: {checker.errors}"
    print(f"✓ All {len(checker.images)} images have alt attributes")


def test_html_structure():
    """HTML構造の基本チェック"""
    class StructureChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.has_doctype = False
            self.has_title = False
            self.has_charset = False

        def handle_decl(self, decl):
            if 'DOCTYPE' in decl.upper():
                self.has_doctype = True

        def handle_starttag(self, tag, attrs):
            if tag == 'title':
                self.has_title = True
            if tag == 'meta':
                attrs_dict = dict(attrs)
                if attrs_dict.get('charset'):
                    self.has_charset = True

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    checker = StructureChecker()
    checker.feed(html)

    assert checker.has_doctype, "Missing DOCTYPE"
    print("✓ Has DOCTYPE")

    assert checker.has_title, "Missing <title>"
    print("✓ Has <title>")

    assert checker.has_charset, "Missing charset"
    print("✓ Has charset declaration")


def test_no_deprecated_attributes():
    """非推奨の属性がないかチェック"""
    class DeprecatedChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.warnings = []

        def handle_starttag(self, tag, attrs):
            attrs_dict = dict(attrs)

            if tag == 'iframe' and 'frameborder' in attrs_dict:
                self.warnings.append('iframe has deprecated frameborder')

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    checker = DeprecatedChecker()
    checker.feed(html)

    assert len(checker.warnings) == 0, f"Deprecated attributes: {checker.warnings}"
    print("✓ No deprecated attributes")


def test_iframe_has_title():
    """iframeにtitle属性があるか（アクセシビリティ）"""
    class IframeChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.iframes = []

        def handle_starttag(self, tag, attrs):
            if tag == 'iframe':
                attrs_dict = dict(attrs)
                self.iframes.append(attrs_dict)

    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    checker = IframeChecker()
    checker.feed(html)

    for iframe in checker.iframes:
        assert 'title' in iframe, f"iframe missing title: {iframe.get('src', '')}"
        print(f"✓ iframe has title: {iframe['title']}")


if __name__ == '__main__':
    runner = TestRunner()

    runner.run_test("File Exists", test_file_exists)
    runner.run_test("All Images Exist", test_all_images_exist)
    runner.run_test("Images Have Alt Text", test_all_images_have_alt)
    runner.run_test("HTML Structure Valid", test_html_structure)
    runner.run_test("No Deprecated Attributes", test_no_deprecated_attributes)
    runner.run_test("iframes Have Title", test_iframe_has_title)

    sys.exit(runner.summary())
