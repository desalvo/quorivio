/** Validated per-widget art theme and effects used by every presentation surface.
 * Persist only enums: never accept custom CSS, network image URLs or arbitrary class names.
 * Authored fill and stroke always win over the decorative presets. */
import type {WidgetTextStyle} from '../../api/src/domain';
export type WidgetArtTheme=NonNullable<WidgetTextStyle['artTheme']>;
export type WidgetArtEffect=NonNullable<WidgetTextStyle['artEffect']>;
const themes=['studio','glass','playful','minimal'] as const;
const effects=['none','float','glow','tilt'] as const;
export type WidgetTimerFace=NonNullable<WidgetTextStyle['timerFace']>;
const timerFaces=['hourglass','dial','digital'] as const;
export function widgetTimerFace(style?:WidgetTextStyle):WidgetTimerFace{
 return timerFaces.includes(style?.timerFace as WidgetTimerFace)?style!.timerFace!:'hourglass';
}
export function widgetArtTheme(style?:WidgetTextStyle):WidgetArtTheme{
 return themes.includes(style?.artTheme as WidgetArtTheme)?style!.artTheme!:'studio';
}
export function widgetArtEffect(style?:WidgetTextStyle):WidgetArtEffect{
 return effects.includes(style?.artEffect as WidgetArtEffect)?style!.artEffect!:'none';
}
export function widgetHasAuthoredFill(style?:WidgetTextStyle):boolean{
 return style?.fillNone===true||style?.fillColor!==undefined||style?.fillOpacity!==undefined||style?.fillMode!==undefined;
}
export function widgetArtData(style?:WidgetTextStyle){return {
 'data-art-theme':style?.artTheme?widgetArtTheme(style):'plain',
 'data-art-effect':widgetArtEffect(style),
 'data-art-custom-fill':widgetHasAuthoredFill(style)?'true':'false'
} as const;}
