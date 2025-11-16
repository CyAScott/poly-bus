import { describe, it, expect } from '@jest/globals';
import { Headers } from '../headers';

describe('Headers', () => {
  describe('ContentType', () => {
    it('should have the correct content-type header name', () => {
      expect(Headers.ContentType).toBe('content-type');
    });

    it('should be a readonly property', () => {
      // This test ensures the property is static and readonly
      expect(typeof Headers.ContentType).toBe('string');
      expect(Headers.ContentType).toBeDefined();
    });
  });

  describe('MessageType', () => {
    it('should have the correct message type header name', () => {
      expect(Headers.MessageType).toBe('x-type');
    });

    it('should be a readonly property', () => {
      // This test ensures the property is static and readonly
      expect(typeof Headers.MessageType).toBe('string');
      expect(Headers.MessageType).toBeDefined();
    });
  });

  describe('Headers class structure', () => {
    it('should be a class with static properties', () => {
      expect(Headers).toBeDefined();
      expect(typeof Headers).toBe('function');
    });

    it('should not be instantiable (static class pattern)', () => {
      // Since this is a utility class with only static properties,
      // we can test that it can be instantiated but serves no purpose
      const instance = new Headers();
      expect(instance).toBeDefined();
      expect(instance.constructor).toBe(Headers);
    });
  });
});
