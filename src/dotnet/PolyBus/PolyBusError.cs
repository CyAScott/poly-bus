namespace PolyBus;

public class PolyBusError(int errorCode, string message) : Exception(message)
{
    public int ErrorCode => errorCode;
}
