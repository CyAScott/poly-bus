/**
 * Represents the type of message.
 */
export enum MessageType {
  /**
   * Command message type.
   * Commands are messages that are sent to and processed by a single endpoint.
   */
  Command,

  /**
   * Event message type.
   * Events are messages that can be processed by multiple endpoints and sent from a single endpoint.
   */
  Event
}
