using Microsoft.AspNetCore.Identity;
using Recycle.Data;
using Recycle.Data.Models;
using Recycle.Interfaces;

namespace Recycle.Services
{
    public class UserServices
    {
        private readonly UserManager<User> userManager;
        private readonly RewardServices rewardServices;
        public UserServices(UserManager<User> userManager, RewardServices rewardServices)
        {
            this.userManager = userManager;
            this.rewardServices = rewardServices;
        }

        public async Task<double> Getcoins(string id ) {

            var user = await userManager.FindByIdAsync(id);
            if (user == null)
            {
                throw new Exception("User not found");
            }
            else
            {
                // Available balance = coins earned minus coins already redeemed.
                var coins = rewardServices.GetAvailableCoins(user.Id);
                user.Coins = coins;
                await userManager.UpdateAsync(user);
                return coins;
            }





        }
    }
}
