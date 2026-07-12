using Recycle.Interfaces;
using Recycle.Data;
using Recycle.Data.Models;
using Recycle.Dtos;
using Microsoft.EntityFrameworkCore;

namespace Recycle.Repos
{
    public class OtpRepo : IOtp
    {
        private readonly Context _context;
        public OtpRepo(Context context)
        {
            this.
                _context = context;
        }

        public IQueryable<Otp> GetAllOtps()
        {
            return _context.Otps.AsQueryable();
        }

        public Otp? GetByCode(string code)
        {
            return _context.Otps.Include(o => o.User).FirstOrDefault(o => o.Code == code);
        }

        public void SetOtpUser(int otpid, string userId)
        {
            var existingOtp = _context.Otps.FirstOrDefault(o => o.Id == otpid);
            if (existingOtp != null)
            {
                existingOtp.UserId = userId;
                existingOtp.IsUsed = true;   // paired
                _context.SaveChanges();
            }
        }

        public void AddOtp(AddOtp otp, string? userid)
        {
            var newotp = new Otp
            {
                MachineId= otp.MachineId,
                Code = otp.Code,
                UserId = userid,
                ExpireAt = otp.ExpireAt,
                IsUsed = otp.IsUsed,
                Status = otp.Status

            };

            _context.Otps.Add(newotp);
            _context.SaveChanges();
        }

        public void UpdateOtpStatus(UpdateStatusOfOtp otp, int otpid)
        {
            var existingOtp = _context.Otps.FirstOrDefault(o => o.Id == otpid);
            if (existingOtp != null)
            {
                existingOtp.Status = otp.Status;
                _context.SaveChanges();
            }
        }
        public void updateOtpIsUsed(int otpid, bool isUsed)
        {
            var existingOtp = _context.Otps.FirstOrDefault(o => o.Id == otpid);
            if (existingOtp != null)
            {
                existingOtp.IsUsed = isUsed;
                _context.SaveChanges();
            }

        }
    }
}
