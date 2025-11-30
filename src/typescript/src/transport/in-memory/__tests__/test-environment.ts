import { InMemoryMessageBroker } from '../in-memory-message-broker';
import { TestEndpoint } from './test-endpoint';
import { AlphaCommand } from './alpha-command';
import { AlphaEvent } from './alpha-event';
import { JsonHandlers } from '../../transaction/message/handlers/serializers/json-handlers';

/**
 * Test environment for InMemory transport tests
 */
export class TestEnvironment {
  public readonly inMemoryMessageBroker: InMemoryMessageBroker = new InMemoryMessageBroker();
  public readonly alpha: TestEndpoint = new TestEndpoint();
  public readonly beta: TestEndpoint = new TestEndpoint();

  public async setup(): Promise<void> {
    await this.setupEndpoint(this.alpha, 'alpha');
    await this.setupEndpoint(this.beta, 'beta');
  }

  private async setupEndpoint(testEndpoint: TestEndpoint, name: string): Promise<void> {
    const jsonHandlers = new JsonHandlers();

    // add handlers for incoming messages
    testEndpoint.builder.incomingPipeline.push(jsonHandlers.deserializer.bind(jsonHandlers));
    testEndpoint.builder.incomingPipeline.push(testEndpoint.handler.bind(testEndpoint));

    // add messages
    testEndpoint.builder.messages.add(AlphaCommand);
    testEndpoint.builder.messages.add(AlphaEvent);
    testEndpoint.builder.name = name;

    // add handlers for outgoing messages
    testEndpoint.builder.outgoingPipeline.push(jsonHandlers.serializer.bind(jsonHandlers));

    // configure InMemory transport
    testEndpoint.builder.transportFactory = this.inMemoryMessageBroker.addEndpoint.bind(
      this.inMemoryMessageBroker
    );

    // create the bus instance
    testEndpoint.bus = await testEndpoint.builder.build();
  }

  public async start(): Promise<void> {
    await this.alpha.bus.start();
    await this.beta.bus.start();
  }

  public async stop(): Promise<void> {
    await this.alpha.bus.stop();
    await this.beta.bus.stop();
  }
}
