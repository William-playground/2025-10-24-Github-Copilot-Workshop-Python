"""
Unit tests for Point2D class
"""
import pytest
import math
from point import Point2D


class TestPoint2D:
    """Test suite for Point2D class"""
    
    def test_init(self):
        """Test Point2D initialization"""
        point = Point2D(3, 4)
        assert point.x == 3
        assert point.y == 4
    
    def test_init_zero(self):
        """Test Point2D initialization with zeros"""
        point = Point2D(0, 0)
        assert point.x == 0
        assert point.y == 0
    
    def test_init_negative(self):
        """Test Point2D initialization with negative values"""
        point = Point2D(-5, -10)
        assert point.x == -5
        assert point.y == -10
    
    def test_init_float(self):
        """Test Point2D initialization with float values"""
        point = Point2D(3.5, 4.7)
        assert point.x == 3.5
        assert point.y == 4.7
    
    def test_distance_to_same_point(self):
        """Test distance from a point to itself"""
        point1 = Point2D(0, 0)
        point2 = Point2D(0, 0)
        assert point1.distance_to(point2) == 0
    
    def test_distance_to_horizontal(self):
        """Test distance between horizontally aligned points"""
        point1 = Point2D(0, 0)
        point2 = Point2D(5, 0)
        assert point1.distance_to(point2) == 5
    
    def test_distance_to_vertical(self):
        """Test distance between vertically aligned points"""
        point1 = Point2D(0, 0)
        point2 = Point2D(0, 12)
        assert point1.distance_to(point2) == 12
    
    def test_distance_to_diagonal(self):
        """Test distance using Pythagorean theorem (3-4-5 triangle)"""
        point1 = Point2D(0, 0)
        point2 = Point2D(3, 4)
        assert point1.distance_to(point2) == 5
    
    def test_distance_to_negative_coords(self):
        """Test distance with negative coordinates"""
        point1 = Point2D(-3, -4)
        point2 = Point2D(0, 0)
        assert point1.distance_to(point2) == 5
    
    def test_distance_to_symmetric(self):
        """Test that distance is symmetric (A to B = B to A)"""
        point1 = Point2D(1, 2)
        point2 = Point2D(4, 6)
        assert point1.distance_to(point2) == point2.distance_to(point1)
    
    def test_distance_to_float_coordinates(self):
        """Test distance with float coordinates"""
        point1 = Point2D(1.5, 2.5)
        point2 = Point2D(4.5, 6.5)
        expected = math.sqrt((4.5 - 1.5)**2 + (6.5 - 2.5)**2)
        assert abs(point1.distance_to(point2) - expected) < 1e-10
    
    def test_str_representation(self):
        """Test string representation"""
        point = Point2D(3, 4)
        assert str(point) == "Point2D(3, 4)"
    
    def test_str_representation_zero(self):
        """Test string representation with zeros"""
        point = Point2D(0, 0)
        assert str(point) == "Point2D(0, 0)"
    
    def test_str_representation_negative(self):
        """Test string representation with negative values"""
        point = Point2D(-5, -10)
        assert str(point) == "Point2D(-5, -10)"
    
    def test_str_representation_float(self):
        """Test string representation with float values"""
        point = Point2D(3.5, 4.7)
        assert str(point) == "Point2D(3.5, 4.7)"
