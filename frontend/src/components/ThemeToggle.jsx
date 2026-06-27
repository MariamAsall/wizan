import { useTheme } from "next-themes";
import { Button } from "./ui/button";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
    variant="destructive"
    className="font-bold"
      onClick={() =>
        setTheme(theme === "dark" ? "light" : "dark")
      }
    >
        {theme === "dark" ? "Light" : "Dark"}
    </Button>
  );
}