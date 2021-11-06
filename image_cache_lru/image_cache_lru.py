"""Main module."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


@dataclass
class Img:
    name: str
    size: int = 0


@dataclass
class ImgNode:
    img: Img
    prev: Union[ImgNode, None] = None
    next: Union[ImgNode, None] = None

    def chain_prev(self, prev_node: ImgNode):
        self.prev = prev_node

    def chain_next(self, next_node: ImgNode):
        self.next = next_node

    def unchain_prev(self) -> ImgNode:
        node = self.prev
        self.prev = None
        return node

    def unchain_next(self) -> ImgNode:
        node = self.next
        self.next = None
        return node



@dataclass
class ImgManager:
    cache_size: int = 0
    _head_node: Union[ImgNode, None] = None
    _tail_node: Union[ImgNode, None] = None
    _img_map: dict = field(default_factory=dict)
    _free_cache_available: int = field(init=False)

    def __post_init__(self):
        self._free_cache_available = self.cache_size

    def actual_cache_size(self) -> int:
        return self._free_cache_available

    def _take_free_cache_storage(self, size: int) -> int:
        if self._free_cache_available - size < 0:
            raise Exception("attempted to overflow the size of the cache")
        self._free_cache_available -= size
        return self._free_cache_available

    def _recover_cache_storage(self, size: int):
        if self._free_cache_available + size > self.cache_size:
            raise Exception("attempted to recover unassigned storage")
        self._free_cache_available += size
        return self._free_cache_available

    def _cache_image(self, img: Img):
        self._img_map[img.name] = img

    def _remove_from_cache(self, img: Img) -> Img:
        n_img = self._img_map[img.name]
        del self._img_map[img.name]
        return n_img

    def _image_cached(self, key: str) -> Img:
        return self._img_map.get(key, None)

    def _insert_image_on_top(self, img: Img):
        node = ImgNode(img)
        if self._head_node is None:
            self._head_node, self._tail_node = node, node
        else:
            self._head_node.chain_next(node)
            node.chain_prev(self._head_node)
            self._head_node = node

    def _drop_lru_image(self) -> Img:
        if self._tail_node is None:
            raise Exception("no nodes at all.")
        else:
            node = self._tail_node
            next_node = node.unchain_next()
            if next_node:
                assert next_node.unchain_prev() == node
                self._tail_node = next_node
            else:
                self._head_node, self._tail_node = None, None
            return node.img

    def push_image(self, img: Img) -> bool:
        while True:
            if self._image_cached(img.name):
                return True
            if img.size > self.cache_size:
                return False
            if self._free_cache_available - img.size < 0:
                lru_image = self._drop_lru_image()
                self._remove_from_cache(lru_image)
                self._recover_cache_storage(lru_image.size)
            else:
                self._cache_image(img)
                self._take_free_cache_storage(img.size)
                self._insert_image_on_top(img)
                return True

    def get_head_image(self) -> Union[Img, None]:
        if self._head_node:
            return self._head_node.img
        return None

    def get_tail_image(self) -> Union[Img, None]:
        if self._tail_node:
            return self._tail_node.img
        return None

    def get_free_cache_available(self) -> int:
        return self._free_cache_available

    def num_of_cached_imgs(self) -> int:
        return len(self._img_map)
