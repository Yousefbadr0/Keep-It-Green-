namespace Recycle.Dtos
{
    public class ViewVendor
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string? Description { get; set; }
        public string Email { get; set; } = string.Empty;
        public bool IsActive { get; set; }
    }
}
