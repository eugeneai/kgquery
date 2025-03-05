#!/usr/bin/env python

"""Tests for `kgquery` package."""


import unittest

from kgquery import samples


class TestKgquery(unittest.TestCase):
    """Tests for `kgquery` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

    def test_001_query_khuzhir(self):
        """Testing KG query for KHUZHIR site"""
        result = samples("Хужир")
        assert result, "Empty result"
        
        
