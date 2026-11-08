import type {PageDesign} from '../../api/src/domain';
/** Explicit local images/URLs take priority. A master image overrides an ordinary
 * local background colour, so it works on all pages created before the master.
 * An independent authored phone background never inherits the desktop picture. */
export function slideBackground(page:PageDesign|undefined,theme:PageDesign|undefined):{assetId?:string;url?:string;color?:string}{
 if(page?.backgroundAssetId)return {assetId:page.backgroundAssetId};
 if(page?.backgroundUrl)return {url:page.backgroundUrl};
 if(theme?.master?.backgroundAssetId)return {assetId:theme.master.backgroundAssetId};
 const color=page?.backgroundColor||theme?.backgroundColor;
 return color?{color}:{};
}
export function slideBackgroundCss(page:PageDesign|undefined,theme:PageDesign|undefined,assetUrl:(id:string)=>string){
 const chosen=slideBackground(page,theme);
 const fit=page?.importedImageFit||'cover';
 const imageSize=fit==='fill'?'100% 100%':fit;
 const backdrop=page?.importedImageFit?{backgroundColor:'#ffffff',backgroundRepeat:'no-repeat'}:{};
 return chosen.assetId?{...backdrop,backgroundImage:`url("${assetUrl(chosen.assetId)}")`,backgroundSize:imageSize,backgroundPosition:'center'}:
 chosen.url?{...backdrop,backgroundImage:`url("${chosen.url}")`,backgroundSize:imageSize,backgroundPosition:'center'}:
 chosen.color?{backgroundColor:chosen.color}:{};
}
