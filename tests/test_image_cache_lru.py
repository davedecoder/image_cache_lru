#!/usr/bin/env python

"""Tests for `image_cache_lru` package."""
from dataclasses import dataclass
from typing import Tuple, Dict, List

import pytest

from click.testing import CliRunner

from image_cache_lru import image_cache_lru
from image_cache_lru import cli
from image_cache_lru.image_cache_lru import ImgManager, Img


@pytest.fixture
def img_manager() -> ImgManager:
    return ImgManager(cache_size=10)


@dataclass
class ImgTestCase:
    img: Img
    fits_cache: bool = False


@pytest.fixture
def regular_imgs_test_case() -> List:
    imgs = [
        ImgTestCase(
            img=Img(name="img_1", size=3),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_2", size=3),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_3", size=4),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_4", size=20),
            fits_cache=False
        ),
    ]
    return imgs


@pytest.fixture
def imgs_test_case_a() -> List:
    imgs = [
        ImgTestCase(
            img=Img(name="img_1", size=10),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_2", size=3),
            fits_cache=True
        )
    ]
    return imgs


@pytest.fixture
def imgs_test_case_b() -> List:
    imgs = [
        ImgTestCase(
            img=Img(name="img_1", size=3),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_2", size=3),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_3", size=4),
            fits_cache=True
        ), ImgTestCase(
            img=Img(name="img_4", size=10),
            fits_cache=True
        ),
    ]
    return imgs


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'image_cache_lru.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def test_reduce_free_cache_size():
    cache_size = 10
    img_manager = ImgManager(cache_size=cache_size)
    assert img_manager._take_free_cache_storage(10) == 0
    cache_size = 20
    img_manager = ImgManager(cache_size=cache_size)
    img_manager._take_free_cache_storage(5)
    img_manager._take_free_cache_storage(5)
    img_manager._take_free_cache_storage(1)
    assert img_manager.actual_cache_size() == 9
    cache_size = 20
    img_manager = ImgManager(cache_size=cache_size)
    assert img_manager._take_free_cache_storage(0) == cache_size
    with pytest.raises(Exception):
        cache_size = 20
        img_manager = ImgManager(cache_size=cache_size)
        img_manager._take_free_cache_storage(cache_size + 1)


def test_recover_cache_storage():
    cache_size = 10
    img_manager = ImgManager(cache_size=cache_size)
    img_manager._take_free_cache_storage(10)
    assert img_manager._recover_cache_storage(10) == cache_size
    cache_size = 20
    img_manager = ImgManager(cache_size=cache_size)
    img_manager._take_free_cache_storage(5)
    img_manager._take_free_cache_storage(5)
    img_manager._take_free_cache_storage(1)
    img_manager._recover_cache_storage(5)
    img_manager._recover_cache_storage(5)
    img_manager._recover_cache_storage(1)
    assert img_manager.actual_cache_size() == cache_size
    cache_size = 20
    img_manager = ImgManager(cache_size=cache_size)
    assert img_manager._recover_cache_storage(0) == cache_size
    with pytest.raises(Exception):
        cache_size = 20
        img_manager = ImgManager(cache_size=cache_size)
        img_manager._recover_cache_storage(cache_size + 1)


def test_cache_image(regular_imgs_test_case):
    img = ImgManager(cache_size=10)
    for item in regular_imgs_test_case:
        img._cache_image(item.img)
    for item in regular_imgs_test_case:
        assert img._image_cached(item.img.name) == item.img
    for item in regular_imgs_test_case:
        assert img._remove_from_cache(item.img) == item.img
    for item in regular_imgs_test_case:
        assert img._image_cached(item.img.name) is None


def test_grow_node_chain(regular_imgs_test_case, img_manager):
    for item in regular_imgs_test_case:
        img_manager._insert_image_on_top(item.img)

    i = len(regular_imgs_test_case) - 1
    head = img_manager._head_node
    while i:
        if head is None:
            break
        assert head.img == regular_imgs_test_case[i].img
        head = head.prev
        i -= 1
    assert i == 0
    assert head == img_manager._tail_node


def test_drop_lru_node(regular_imgs_test_case, img_manager):
    for item in regular_imgs_test_case:
        img_manager._insert_image_on_top(item.img)
    lru_image = img_manager._drop_lru_image()
    last_inserted_img = regular_imgs_test_case[0].img
    assert lru_image == last_inserted_img
    lru_image = img_manager._drop_lru_image()
    second_last_inserted_img = regular_imgs_test_case[1].img
    assert lru_image == second_last_inserted_img


def test_drop_lru_node_a(regular_imgs_test_case, img_manager):
    for item in regular_imgs_test_case:
        img_manager._insert_image_on_top(item.img)
    i = len(regular_imgs_test_case) - 1
    last_inserted_img = None
    while i >= 0:
        last_inserted_img = img_manager._drop_lru_image()
        i -= 1
    assert last_inserted_img == regular_imgs_test_case[-1].img
    with pytest.raises(Exception):
        img_manager._drop_lru_image()


def test_push_image(regular_imgs_test_case, img_manager):
    for item in regular_imgs_test_case:
        assert img_manager.push_image(item.img) == item.fits_cache


def test_push_image_a(imgs_test_case_a, img_manager):
    for item in imgs_test_case_a:
        assert img_manager.push_image(item.img) == item.fits_cache
    assert img_manager.get_head_image() == imgs_test_case_a[1].img
    assert img_manager.get_tail_image() == imgs_test_case_a[1].img


def test_push_image_aa(imgs_test_case_a, img_manager):
    item = imgs_test_case_a[0]
    assert img_manager.push_image(item.img) == item.fits_cache
    assert img_manager.get_head_image() == imgs_test_case_a[0].img
    assert img_manager.get_tail_image() == imgs_test_case_a[0].img


def test_push_image_b(imgs_test_case_b, img_manager):
    for item in imgs_test_case_b:
        assert img_manager.push_image(item.img) == item.fits_cache
    assert img_manager.get_head_image() == imgs_test_case_b[-1].img
    assert img_manager.get_tail_image() == imgs_test_case_b[-1].img
    assert img_manager.get_free_cache_available() == 0
    assert img_manager.num_of_cached_imgs() == 1
