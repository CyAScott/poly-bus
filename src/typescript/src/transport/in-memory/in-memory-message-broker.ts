/* eslint-disable no-undef */

import { InMemoryEndpoint } from './in-memory-endpoint';
import { IPolyBus } from '../../i-poly-bus';
import { ITransport } from '../i-transport';
import { PolyBusBuilder } from '../../poly-bus-builder';
import { Transaction } from '../transaction/transaction';
import { IncomingMessage } from '../transaction/message/incoming-message';

/**
 * A message broker that uses in-memory transport for message passing.
 */
export class InMemoryMessageBroker {
  /**
   * The collection of in-memory endpoints managed by this broker.
   */
  public readonly endpoints = new Map<string, InMemoryEndpoint>();

  /**
   * The ITransport factory method.
   */
  public async addEndpoint(_builder: PolyBusBuilder, bus: IPolyBus): Promise<ITransport> {
    const endpoint = new InMemoryEndpoint(this, bus);
    this.endpoints.set(bus.name, endpoint);
    return endpoint;
  }

  /**
   * Processes the transaction and distributes outgoing messages to the appropriate endpoints.
   */
  public send(transaction: Transaction): void {
    if (transaction.outgoingMessages.length === 0) {
      return;
    }

    // Execute asynchronously without blocking
    void (async () => {
      try {
        await this.processTransaction(transaction);
      } catch (error) {
        console.error('Error processing transaction:', error);
      }
    })();
  }

  private async processTransaction(transaction: Transaction): Promise<void> {
    const tasks: Promise<void>[] = [];
    const now = new Date();

    for (const message of transaction.outgoingMessages) {
      for (const endpoint of this.endpoints.values()) {
        const isDeadLetter = endpoint.deadLetterEndpoint === message.endpoint;

        if (
          isDeadLetter ||
          endpoint.bus.name === message.endpoint ||
          (message.endpoint === undefined &&
            (message.messageInfo.endpoint === endpoint.bus.name ||
              endpoint.isSubscribed(message.messageInfo)))
        ) {
          const incomingMessage = new IncomingMessage(
            endpoint.bus,
            message.body,
            message.messageInfo
          );
          incomingMessage.headers = new Map(message.headers);

          if (message.deliverAt) {
            const delay = message.deliverAt.getTime() - now.getTime();
            if (delay > 0) {
              this.delayedSend(endpoint, incomingMessage, delay, isDeadLetter);
              continue;
            }
          }

          const task = endpoint.handleMessage(incomingMessage, isDeadLetter);
          tasks.push(task);
        }
      }
    }

    await Promise.all(tasks);
  }

  private delayedSend(
    endpoint: InMemoryEndpoint,
    message: IncomingMessage,
    delay: number,
    isDeadLetter: boolean
  ): void {
    const timeoutId = setTimeout(async () => {
      try {
        if (!this._stopped) {
          await endpoint.handleMessage(message, isDeadLetter);
        }
      } catch (error) {
        console.error('Error delivering delayed message:', error);
      } finally {
        this._timeouts.delete(timeoutId);
      }
    }, delay);
    this._timeouts.add(timeoutId);
  }

  /**
   * Stops all endpoints and waits for in-flight messages to be processed.
   */
  public async stop(): Promise<void> {
    this._stopped = true;

    for (const endpoint of this.endpoints.values()) {
      await endpoint.stop();
    }

    // Cancel all delayed messages
    for (const timeoutId of this._timeouts) {
      clearTimeout(timeoutId);
    }
    this._timeouts.clear();
  }

  private _stopped: boolean = false;
  private readonly _timeouts = new Set<NodeJS.Timeout>();
}
