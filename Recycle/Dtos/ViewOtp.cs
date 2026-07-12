using System.ComponentModel.DataAnnotations.Schema;

namespace Recycle.Dtos
{
    public class ViewOtp
    {
        public int Id { get; set; }

        public int MachineId { get; set; }
        public string? UserId { get; set; }
    }
}
