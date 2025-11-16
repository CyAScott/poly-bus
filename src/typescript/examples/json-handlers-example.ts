import { PolyBusBuilder, JsonHandlers, MessageType, messageInfo } from '../src/index';

// Example message class with metadata
@messageInfo(MessageType.Command, 'user-service', 'CreateUser', 1, 0, 0)
class CreateUserCommand {
    constructor(
        public readonly name: string,
        public readonly email: string
    ) {}
}

// Example of configuring JsonHandlers with PolyBus
async function setupJsonHandlers() {
    const builder = new PolyBusBuilder();
    
    // Create JsonHandlers instance with custom configuration
    const jsonHandlers = new JsonHandlers();
    jsonHandlers.contentType = 'application/json';
    jsonHandlers.throwOnMissingType = true;
    jsonHandlers.throwOnInvalidType = true;
    
    // Optional: Configure custom JSON processing
    jsonHandlers.jsonReplacer = (key: string, value: any) => {
        // Custom serialization logic if needed
        if (key === 'password') {
            return undefined; // Remove password fields during serialization
        }
        return value;
    };
    
    jsonHandlers.jsonReviver = (key: string, value: any) => {
        // Custom deserialization logic if needed
        if (key === 'createdAt' && typeof value === 'string') {
            return new Date(value); // Convert ISO strings to Date objects
        }
        return value;
    };
    
    // Add JsonHandlers to the incoming and outgoing pipeline
    builder.incomingHandlers.push(jsonHandlers.deserializer.bind(jsonHandlers));
    builder.outgoingHandlers.push(jsonHandlers.serializer.bind(jsonHandlers));
    
    // Register message types
    builder.messages.add(CreateUserCommand);
    
    // Build and configure the bus
    const bus = await builder.build();
    
    return bus;
}

// Example usage
async function example() {
    try {
        const bus = await setupJsonHandlers();
        await bus.start();
        
        // Create and send a message
        const transaction = await bus.createTransaction();
        const command = new CreateUserCommand('John Doe', 'john@example.com');
        transaction.addOutgoingMessage(command);
        
        await transaction.commit();
        
        console.log('Message sent successfully');
        
        await bus.stop();
    } catch (error) {
        console.error('Error:', error);
    }
}

// Run the example
if (require.main === module) {
    example().catch(console.error);
}

export { setupJsonHandlers, CreateUserCommand, example };