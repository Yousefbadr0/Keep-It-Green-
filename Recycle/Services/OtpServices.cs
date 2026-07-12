using Recycle.Dtos;
using Recycle.Interfaces;
using System.Security.Cryptography;
using Recycle.Data.Models;

namespace Recycle.Services
{
    public class OtpServices
    {
        private readonly IOtp _otpRepo;
        public OtpServices(IOtp otpRepo)
        {
            _otpRepo = otpRepo;
        }
        public string GenerateOtp(string userid, int machineid)
        {

            string otp;
            do
            {
                otp = RandomNumberGenerator.GetInt32(100000, 1000000).ToString();
            }
            while (_otpRepo.GetAllOtps().Any(o => o.Code == otp && o.Status == StatusOtp.Active && o.IsUsed == false));

            var otpobj = new AddOtp
            {
                Code = otp,
                MachineId = machineid,
                IsUsed = false,
                ExpireAt = DateTime.UtcNow.AddMinutes(5),
                Status = StatusOtp.Active,


            };
            _otpRepo.AddOtp(otpobj, userid);
            return otp;
        }

        public ViewOtp? VerfiyOtp(string otp)
        {
            var existingotp = _otpRepo.GetAllOtps().FirstOrDefault(o => o.Code == otp && o.Status == StatusOtp.Active && o.IsUsed == false);
            if (existingotp != null && existingotp.ExpireAt > DateTime.UtcNow)
            {


                _otpRepo.updateOtpIsUsed(existingotp.Id, true);

                return new ViewOtp
                {


                    Id = existingotp.Id,
                    MachineId = existingotp.MachineId,
                    UserId = existingotp.UserId
                };

            }
            else
            {
                return null;
            }


        }

        public string CheckBeforGenerationOtp(string userid, int machineid)
        {

            var otps = _otpRepo.GetAllOtps().Where(o => o.UserId == userid && o.Status == StatusOtp.Active && o.IsUsed == false && o.ExpireAt > DateTime.UtcNow).ToList();
            if (otps.Count == 0)
            {
                return GenerateOtp(userid, machineid);
            }

            else
            {
                foreach (var item in otps)

                {
                    var status = new UpdateStatusOfOtp
                    {

                        Status = StatusOtp.Stopped
                    };
                    _otpRepo.UpdateOtpStatus(status, item.Id);

                }

                return GenerateOtp(userid, machineid);



            }

        }

        /// <summary>
        /// Resolves the active session for a given OTP code (used by the machine flow).
        /// Verifies the OTP on first use, then allows multiple item submissions while the
        /// session stays Active and unexpired. Returns null if the code is invalid/expired.
        /// </summary>
        public ViewOtp? ResolveActiveSession(string code)
        {
            var otp = _otpRepo.GetAllOtps()
                .FirstOrDefault(o => o.Code == code
                                  && o.Status == StatusOtp.Active
                                  && o.UserId != null            // must be paired with a user
                                  && o.ExpireAt > DateTime.UtcNow);
            if (otp == null)
                return null;

            return new ViewOtp
            {
                Id = otp.Id,
                MachineId = otp.MachineId,
                UserId = otp.UserId
            };
        }

        // ─── Machine-started session (ATM-style QR pairing) ───────────────────────

        /// <summary>Machine starts a session: creates a pending pairing code (no user yet).</summary>
        public string StartMachineSession(int machineId)
        {
            string code;
            do
            {
                code = RandomNumberGenerator.GetInt32(100000, 1000000).ToString();
            }
            while (_otpRepo.GetAllOtps().Any(o => o.Code == code && o.Status == StatusOtp.Active && o.UserId == null));

            _otpRepo.AddOtp(new AddOtp
            {
                Code = code,
                MachineId = machineId,
                IsUsed = false,
                ExpireAt = DateTime.UtcNow.AddMinutes(15),
                Status = StatusOtp.Active,
            }, null);
            return code;
        }

        /// <summary>User pairs with a machine session by scanning the QR / typing the code.</summary>
        public ViewOtp PairSession(string code, string userId)
        {
            var otp = _otpRepo.GetByCode(code);
            if (otp == null || otp.Status != StatusOtp.Active || otp.ExpireAt <= DateTime.UtcNow)
                throw new InvalidOperationException("Invalid or expired code.");
            if (otp.UserId != null)
                throw new InvalidOperationException("This session is already in use.");

            _otpRepo.SetOtpUser(otp.Id, userId);
            return new ViewOtp { Id = otp.Id, MachineId = otp.MachineId, UserId = userId };
        }

        /// <summary>The user bound to a session code (null if unpaired/unknown).</summary>
        public string? GetUserId(string code) => _otpRepo.GetByCode(code)?.UserId;

        /// <summary>Stops the user's active session(s) — called when they tap "Finish" on the
        /// phone, so the machine's status poll sees it end and returns to idle.</summary>
        public int EndUserSessions(string userId)
        {
            var otps = _otpRepo.GetAllOtps()
                .Where(o => o.UserId == userId && o.Status == StatusOtp.Active)
                .ToList();
            foreach (var o in otps)
                _otpRepo.UpdateOtpStatus(new UpdateStatusOfOtp { Status = StatusOtp.Stopped }, o.Id);
            return otps.Count;
        }

        /// <summary>Ends the session identified by a pairing code — called by the MACHINE when it
        /// finishes or times out, so the phone's poll sees it end too (two-way close).</summary>
        public int EndSessionByCode(string code)
        {
            var otp = _otpRepo.GetByCode(code);
            if (otp?.UserId != null)
                return EndUserSessions(otp.UserId);
            if (otp != null && otp.Status == StatusOtp.Active)
            {
                _otpRepo.UpdateOtpStatus(new UpdateStatusOfOtp { Status = StatusOtp.Stopped }, otp.Id);
                return 1;
            }
            return 0;
        }

        /// <summary>Does this user currently have a live paired session? The phone polls this so it
        /// auto-closes when the machine ends the session (no manual Finish tap needed).</summary>
        public bool UserHasActiveSession(string userId)
        {
            return _otpRepo.GetAllOtps().Any(o => o.UserId == userId
                && o.Status == StatusOtp.Active && o.ExpireAt > DateTime.UtcNow);
        }

        /// <summary>Machine polls this after showing the QR; returns once a user has paired.</summary>
        public (bool paired, string? userName) GetSessionStatus(string code)
        {
            var otp = _otpRepo.GetByCode(code);
            if (otp == null || otp.Status != StatusOtp.Active || otp.ExpireAt <= DateTime.UtcNow)
                return (false, null);
            return (otp.UserId != null, otp.User?.UserName);
        }

        /// <summary>Read-only check: is this OTP code a live, unexpired session? Does not consume it.</summary>
        public bool IsActiveOtp(string code)
        {
            return _otpRepo.GetAllOtps()
                .Any(o => o.Code == code
                       && o.Status == StatusOtp.Active
                       && o.ExpireAt > DateTime.UtcNow);
        }

        public void UpdateOtp(UpdateStatusOfOtp status, int otpId)
        {

            _otpRepo.UpdateOtpStatus(status, otpId);





        }
    }
}
