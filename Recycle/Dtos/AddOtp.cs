using Recycle.Data.Models;

namespace Recycle.Dtos
{
    public class AddOtp
    {
        public string UserId { get; set; } = string.Empty;
        public string Code { get; set; } = string.Empty;
        public int MachineId { get; set; }

        public DateTime ExpireAt { get; set; }

        public bool IsUsed { get; set; }

        public StatusOtp Status { get; set; }
    }
}
