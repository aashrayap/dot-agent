# Devon Energy Brand Standards

Official brand guidelines for Devon Energy projects and materials.

## Brand Values

Devon's core values guide all communications:

| Value | Description |
|-------|-------------|
| **Integrity** | Openness and honesty at the core of everything |
| **Relationships** | Caring, connected, supportive - succeed as one team |
| **Courage** | Take intelligent risks, share successes and failures |
| **Results** | Achieve better results, make positive sustainable impact |

## Brand Voice

**How we communicate:**

- **Think**: strategic, future-forward, prudent, measured, determined
- **Speak**: authentic, clear, purposeful, thoughtful; no buzzwords or ambiguity
- **Work**: intentional, energetic, focused, enthusiastic
- **Lead**: strong yet understated; earn attention through contribution
- **Give Back**: build relationships, meaningful impact, strategic giving

## Color Palette

### Primary Colors

Use these first.

| Name | Hex | RGB | CMYK | Pantone |
|------|-----|-----|------|---------|
| Clay Orange | `#F04123` | 240, 65, 35 | 0, 90, 100, 0 | 2028 CP |
| Flint Gray | `#969B9B` | 150, 155, 155 | 44, 33, 35, 1 | Cool Gray 7 CP |
| Slate Gray | `#4B4F54` | 75, 79, 84 | 69, 59, 53, 33 | 4140 CP |
| Iron Black | `#212121` | 33, 33, 33 | 72, 66, 65, 73 | Black 6 CP |

### Secondary Colors

Supporting role only.

| Name | Hex | RGB | CMYK | Pantone |
|------|-----|-----|------|---------|
| Midnight Blue | `#003366` | 0, 51, 102 | 100, 87, 33, 23 | 541 CP |
| Sky Blue | `#99CCFF` | 153, 204, 255 | 35, 10, 0, 0 | 2905 CP |
| Forest Green | `#476B2B` | 71, 107, 43 | 73, 36, 100, 25 | 4216 CP |
| Grass Green | `#BBE25A` | 187, 226, 90 | 31, 0, 80, 0 | 2298 CP |
| Neutral Sand | `#DDC6B6` | 221, 198, 182 | 13, 21, 26, 0 | 7604 CP |
| Neutral Air | `#F4F4F4` | 244, 244, 244 | 3, 2, 2, 0 | 663 CP |

**Important:** Use colors at 100%. Tints are allowed only for data
visualizations.

## Typography

### Primary Typeface (Headlines)

**Tusker Grotesque 5600 Semibold**

- high-impact, commanding x-height, condensed proportions
- use for headlines
- conveys strength and confidence

### Secondary Typeface (Body)

**Aeonik**

- sans-serif, clean lines, geometric shapes
- light to bold weights available
- use for body text and subheads

### Web and Email Fallback

**DM Sans**: [Google Fonts](https://fonts.google.com/specimen/DM+Sans)

### PowerPoint Fallbacks

- **Headlines**: Impact Regular (always capitalized)
- **Subheads and body emphasis**: Arial Bold or Medium
- **Body**: Arial Regular

### Hierarchy Rules

- Headlines: bold, larger sizes, command attention
- Subheads: provide context, break content into sections
- Body: legible, readable font size

## CSS Variables

```css
:root {
  /* Primary */
  --devon-clay-orange: #F04123;
  --devon-flint-gray: #969B9B;
  --devon-slate-gray: #4B4F54;
  --devon-iron-black: #212121;

  /* Secondary */
  --devon-midnight-blue: #003366;
  --devon-sky-blue: #99CCFF;
  --devon-forest-green: #476B2B;
  --devon-grass-green: #BBE25A;
  --devon-neutral-sand: #DDC6B6;
  --devon-neutral-air: #F4F4F4;

  /* Typography */
  --devon-font-headline: 'Tusker Grotesque', Impact, sans-serif;
  --devon-font-body: 'Aeonik', 'DM Sans', Arial, sans-serif;
}
```

## Tailwind Config

```javascript
module.exports = {
  theme: {
    extend: {
      colors: {
        devon: {
          orange: '#F04123',
          'flint-gray': '#969B9B',
          'slate-gray': '#4B4F54',
          'iron-black': '#212121',
          'midnight-blue': '#003366',
          'sky-blue': '#99CCFF',
          'forest-green': '#476B2B',
          'grass-green': '#BBE25A',
          sand: '#DDC6B6',
          air: '#F4F4F4',
        }
      },
      fontFamily: {
        'devon-headline': ['Tusker Grotesque', 'Impact', 'sans-serif'],
        'devon-body': ['Aeonik', 'DM Sans', 'Arial', 'sans-serif'],
      }
    }
  }
}
```

## Logo Guidelines

### Logo Components

- **Strata Bars**: represent Earth's geological layers, from Oklahoma red dirt
  to bedrock
- **Wordmark**: `devon`
- Together they form the Devon Signature

### Minimum Sizes

- Print: never smaller than 1 inch
- Digital: never smaller than 72px
- Alternate signature (signage or embroidery): never smaller than 0.375 inch

### Clear Space

- Minimum clear space = height of the letter `o` in the wordmark (1x)
- Maintain 1x on all sides; prefer more when possible

### Logo Don'ts

- do not scale individual elements separately
- do not distort, rotate, or resize disproportionately
- do not alter spacing between Strata Bars and Wordmark
- do not change colors outside the primary palette
- do not change the position of Strata Bars
- do not use the Wordmark by itself
- do not use different typefaces for the Wordmark
- do not place the logo over busy images
- do not add drop shadows

### Strata Bars Icon

Can be used standalone for:

- social media profile images
- website favicons
- places where the full signature is too large

## Icon Guidelines

### Style

- technical yet friendly
- bold geometric shapes with vibrant colors
- two stroke sizes per icon
- consistent and symmetrical

### Sizes

- Large: 200px max dimension, 10px main stroke, 7.5px secondary stroke
- Small: 38px max dimension, 2px main stroke, 1.5px secondary stroke

### Color Treatment

- line with darker color, fill with lighter color
- greyscale: Iron Black at 30% opacity

## Photography Guidelines

### Categories

1. **People**: relationships, authentic moments, diversity
2. **Innovation and Technology**: real Devon technology, user-centric, dynamic
3. **Field**: clean, bright, respectable, nature
4. **Environment**: energetic, active, determined

### Tone

- authentic, elevated, inspiring
- avoid stock or posed feeling
- natural light preferred
- warm tones: earthy hues, oranges, blues

### Do

- use natural light and golden hour when possible
- show genuine interactions and candid moments
- feature diversity across ethnicity, age, gender, and ability
- choose images with movement and visual interest

### Don't

- artificial lens flares or harsh flash
- overly posed or inauthentic shots
- excessively dirty hands, clothes, or faces in field photos
- proprietary technology

## Accessibility

Follow WCAG guidance for all web content:

- maintain sufficient color contrast ratios
- design for auditory, cognitive, neurological, physical, speech, and visual
  disabilities
- reference: [W3C accessibility principles](https://www.w3.org/WAI/fundamentals/accessibility-principles/)

## Legal

### Trademark Usage

- Correct: `Devon Energy®`
- Incorrect: `Devon Energy® Corporation`

### Copyright Format

```text
© [First Year], [Current Year]
Devon Energy Corporation. All rights reserved.
```

## Brand Resources

**Brand Resource Center (BRC)**:
[devonenergy.bynder.com](https://devonenergy.bynder.com)

Download official assets from the BRC:

- logo files (PNG, SVG, EPS)
- Strata Bars icon
- icon library
- typography files
- PowerPoint templates
- topographic textures

## Quick Reference

| Element | Value |
|---------|-------|
| Primary accent | Clay Orange `#F04123` |
| Body text | Slate Gray `#4B4F54` |
| Headings | Iron Black `#212121` |
| Light background | Neutral Air `#F4F4F4` |
| Headline font | Tusker Grotesque 5600 Semibold |
| Body font | Aeonik |
| Web fallback font | DM Sans |
| Min logo size (digital) | 72px |
| Logo clear space | 1x (height of `o`) |

## Typical Activation

- creating UI components, themes, or design systems
- styling web or mobile applications
- building dashboards or data visualizations
- creating presentations
- writing documents or communications
- generating CSS, SCSS, Tailwind, or design tokens
- reviewing designs for brand compliance
- any work requiring Devon visual identity
