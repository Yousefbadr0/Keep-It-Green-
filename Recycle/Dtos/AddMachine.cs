namespace Recycle.Dtos
{
    public class AddMachine
    {
        public string Name { get; set; } = string.Empty;
        public string Location { get; set; } = string.Empty;

        public bool IsAvailable { get; set; }
    }
}
