import { messageInfo } from '../../transaction/message/message-info';
import { MessageType } from '../../transaction/message/message-type';

/**
 * Test event message for alpha endpoint
 */
@messageInfo(MessageType.Event, 'alpha', 'alpha-event', 1, 0, 0)
export class AlphaEvent {
  public name!: string;
}
