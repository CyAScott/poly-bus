import { messageInfo } from '../../transaction/message/message-info';
import { MessageType } from '../../transaction/message/message-type';

/**
 * Test command message for alpha endpoint
 */
@messageInfo(MessageType.Command, 'alpha', 'alpha-command', 1, 0, 0)
export class AlphaCommand {
  public name!: string;
}
