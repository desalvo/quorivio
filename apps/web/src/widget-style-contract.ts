/** Compile-time regression: the editor must accept all persisted appearance fields.
 * Keep aligned with the API's authoritative WidgetTextStyle validator. */
import type {WidgetTextStyle} from '../../api/src/domain';
import type {WidgetAppearance} from './widget-appearance';

type Equal<A,B> = (<T>()=>T extends A?1:2) extends (<T>()=>T extends B?1:2)?true:false;
type Assert<T extends true> = T;
export type FillModeSchemaParity = Assert<Equal<WidgetAppearance['fillMode'],WidgetTextStyle['fillMode']>>;
export type FillAssetSchemaParity = Assert<Equal<WidgetAppearance['fillImageAssetId'],WidgetTextStyle['fillImageAssetId']>>;
export type ShapeSchemaParity = Assert<Equal<WidgetAppearance['shapeType'],WidgetTextStyle['shapeType']>>;
export type FillOpacitySchemaParity = Assert<Equal<WidgetAppearance['fillOpacity'],WidgetTextStyle['fillOpacity']>>;

// A real style object passed through the editor's typed widget history.
export const compileTimeWidgetFill:WidgetTextStyle = {
 fillMode:'image',fillImageAssetId:'8e763f69-9915-4591-b561-177322052709',
 fillOpacity:0.7,shapeType:'speech',gradientEndColor:'#ffffff',
};
