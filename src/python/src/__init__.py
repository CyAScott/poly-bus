"""Poly Bus - A polyglot message bus library."""

__version__ = "0.1.0"
__author__ = "Poly Bus Contributors"
__email__ = "cy.a.scott@live.com"

# Main entry points
from .poly_bus_builder import PolyBusBuilder
from .i_poly_bus import IPolyBus

__all__ = ["PolyBusBuilder", "IPolyBus"]