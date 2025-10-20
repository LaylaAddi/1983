# App Icons for PWA

## Required Icons

Your PWA needs two icon files to display properly when installed:

1. **icon-192.png** (192x192 pixels)
2. **icon-512.png** (512x512 pixels)

## How to Create Icons

### Option 1: Use Online Generator (Easiest)

Visit: **https://realfavicongenerator.net/**
1. Upload your logo or design
2. Download the generated icons
3. Rename them to `icon-192.png` and `icon-512.png`
4. Place them in this directory (`/static/images/`)

### Option 2: Use Design Tool

Use Figma, Canva, or Photoshop:
- Create a square canvas (512x512 pixels)
- Design your icon (use your app logo or the gavel ⚖️ icon)
- Use your app theme color (#007bff blue)
- Export as PNG with transparency
- Create both sizes: 192x192 and 512x512

### Option 3: Simple Text Icon

For a quick placeholder, you can use a simple design:
- Background: #007bff (blue)
- Text: "1983" in white, bold, centered
- Save as PNG

## Design Tips

✅ **Do:**
- Keep it simple and recognizable
- Use high contrast colors
- Center the main element
- Include padding (safe area)
- Use PNG format with transparency
- Make it square (1:1 aspect ratio)

❌ **Don't:**
- Use small text (hard to read on small icons)
- Use complex gradients
- Include too much detail
- Use low contrast colors
- Use rectangular shapes

## Icon Specifications

### icon-192.png
- **Size:** 192x192 pixels
- **Format:** PNG
- **Use:** Home screen icon on most devices
- **Purpose:** Main app icon

### icon-512.png
- **Size:** 512x512 pixels
- **Format:** PNG
- **Use:** High-resolution displays, splash screen
- **Purpose:** Detailed app icon for large displays

## Current Status

⚠️ **Icons not yet created**

The PWA will work without icons, but browsers will show:
- A default icon, OR
- A screenshot of your site

For the best user experience, create proper icons!

## Testing Icons

After creating icons:

1. Place them in `/static/images/`
2. Run: `python manage.py collectstatic`
3. Clear browser cache
4. Visit `/pwa-demo/` to verify
5. Reinstall the PWA on your phone
6. Check the home screen icon

## Example Icon Designs

### Simple Text Icon
```
+------------------+
|                  |
|                  |
|      1983        |
|                  |
|                  |
+------------------+
Background: #007bff
Text: White, bold
```

### Gavel Icon
```
+------------------+
|                  |
|        ⚖️        |
|      1983        |
|                  |
|                  |
+------------------+
Icon: ⚖️ (white gavel)
Text: 1983 (white)
Background: #007bff
```

### Legal Scale Icon
```
+------------------+
|                  |
|     ⚖️ LEGAL     |
|       1983       |
|                  |
|                  |
+------------------+
```

## Resources

- [Icon Generator](https://realfavicongenerator.net/)
- [PWA Icon Guidelines](https://web.dev/add-manifest/#icons)
- [Figma](https://www.figma.com/) - Free design tool
- [Canva](https://www.canva.com/) - Easy icon creator

---

**Note:** Until you create proper icons, the PWA will still work perfectly! The icons are just for aesthetics when the app is installed on the home screen.
