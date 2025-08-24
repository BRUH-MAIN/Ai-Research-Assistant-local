# Fira Code Nerd Font Setup

## What was configured:

1. **layout.tsx**: Updated to import and use Fira Code from Google Fonts
2. **tailwind.config.ts**: Configured font families to use Fira Code for both sans and mono
3. **globals.css**: Set Fira Code as the default font for the entire application

## To install Fira Code Nerd Font locally (optional but recommended):

### On Linux (your current system):
```bash
# Download and install Fira Code Nerd Font
mkdir -p ~/.local/share/fonts
cd ~/.local/share/fonts
wget https://github.com/ryanoasis/nerd-fonts/releases/download/v3.1.1/FiraCode.zip
unzip FiraCode.zip
rm FiraCode.zip
fc-cache -fv
```

### Alternative methods:
- **Ubuntu/Debian**: `sudo apt install fonts-firacode`
- **Arch Linux**: `sudo pacman -S ttf-fira-code`
- **From Nerd Fonts**: Visit https://www.nerdfonts.com/font-downloads and download FiraCode

## Verification:
After running the development server (`npm run dev`), all text in your application should now use Fira Code font, including:
- Body text
- Buttons
- Input fields
- Code blocks
- All UI components

## Font fallbacks:
The configuration includes proper fallbacks:
1. Fira Code (from Google Fonts)
2. FiraCode Nerd Font (if installed locally)
3. Generic monospace font

This ensures your application will work even if the font fails to load.
