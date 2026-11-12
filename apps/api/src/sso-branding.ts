/** Self-hosted SSO presentation, separate from identity and authorization.
 * Only raster data URLs are accepted for custom providers: never fetch a
 * provider-supplied URL and never render untrusted SVG/HTML.
 */
export const SSO_BRANDS={
 google:{label:'Google',color:'#FFFFFF',text:'#202124',icon:'google'},
 github:{label:'GitHub',color:'#24292F',text:'#FFFFFF',icon:'github'},
 facebook:{label:'Facebook',color:'#1877F2',text:'#FFFFFF',icon:'facebook'},
 microsoft:{label:'Microsoft Entra ID',color:'#3468A3',text:'#FFFFFF',icon:'microsoft'},
 okta:{label:'Okta',color:'#006DAD',text:'#FFFFFF',icon:'okta'},
 keycloak:{label:'Keycloak',color:'#293C69',text:'#FFFFFF',icon:'keycloak'},
 authentik:{label:'Authentik',color:'#195C67',text:'#FFFFFF',icon:'authentik'}
} as const;
export type SsoBrandId=keyof typeof SSO_BRANDS;
export function isBuiltinSsoBrand(id:string):id is SsoBrandId{
 return Object.prototype.hasOwnProperty.call(SSO_BRANDS,id);
}
const COLOUR=/^#[0-9a-fA-F]{6}$/;
export function validSsoLogoData(data:unknown):data is string{
 if(typeof data!=='string'||data.length>46000)return false;
 const m=/^data:image\/(png|jpeg|webp);base64,([A-Za-z0-9+/]+={0,2})$/.exec(data);
 if(!m)return false;
 const bytes=Buffer.from(m[2],'base64');
 if(bytes.length<16||bytes.length>32768||bytes.toString('base64')!==m[2])return false;
 if(m[1]==='png')return bytes.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))&&bytes.toString('ascii',12,16)==='IHDR';
 if(m[1]==='jpeg')return bytes[0]===255&&bytes[1]===216&&bytes.at(-2)===255&&bytes.at(-1)===217;
 return bytes.toString('ascii',0,4)==='RIFF'&&bytes.toString('ascii',8,12)==='WEBP';
}
export function validateSsoBranding(id:string,config:Record<string,unknown>){
 if(config.buttonColor!==undefined&&(typeof config.buttonColor!=='string'||!COLOUR.test(config.buttonColor)))throw Error('invalid_sso_button_color');
 if(config.logoData!==undefined){
  if(isBuiltinSsoBrand(id))throw Error('invalid_sso_builtin_logo');
  if(config.logoData!==''&&!validSsoLogoData(config.logoData))throw Error('invalid_sso_custom_logo');
 }
}
function readableText(bg:string):string{
 const rgb=[1,3,5].map(i=>parseInt(bg.slice(i,i+2),16)/255);
 const light=rgb.map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);
 return (.2126*light[0]+.7152*light[1]+.0722*light[2])>.18?'#101927':'#FFFFFF';
}
export function publicSsoBranding(id:string,config:Record<string,unknown>={}){
 const preset=isBuiltinSsoBrand(id)?SSO_BRANDS[id]:null;
 const defaultColor=preset?.color||'#295C6C';
 const buttonColor=typeof config.buttonColor==='string'&&COLOUR.test(config.buttonColor)?config.buttonColor:defaultColor;
 const textColor=buttonColor===defaultColor&&preset?preset.text:readableText(buttonColor);
 const logoSrc=preset?'/sso-icons/'+preset.icon+'.svg':validSsoLogoData(config.logoData)?config.logoData:undefined;
 return {logoSrc,buttonColor,textColor};
}
