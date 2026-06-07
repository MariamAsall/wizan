import { useTheme } from "next-themes";
import { Button } from "./ui/button";

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme();

  return (
    <Button
      onClick={() =>
        setTheme(theme === "dark" ? "light" : "dark")
      }
    >
        {theme === "dark" ? "Light" : "Dark"}
    </Button>
  );
}