using Recycle.Data.Models;
using Recycle.Dtos;

namespace Recycle.Interfaces
{
    public interface IOtp
    {
        IQueryable<Otp> GetAllOtps();
        void AddOtp(AddOtp otp, string? userId);
        void UpdateOtpStatus(UpdateStatusOfOtp otp, int otpid);
        void updateOtpIsUsed(int otpid, bool isUsed);

        // Machine-started session pairing
        Otp? GetByCode(string code);
        void SetOtpUser(int otpid, string userId);
    }
}
