import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {validPageDesign,validPresenterProfileFontStyle} from '../../api/src/domain.ts';
import {presenterProfileScale} from '../src/presenter-profile-fit.ts';
import {publicSsoBranding,validSsoLogoData,validateSsoBranding} from '../../api/src/sso-branding.ts';
const ui=readFileSync(new URL('../src/main.tsx',import.meta.url),'utf8');
const css=readFileSync(new URL('../src/style.css',import.meta.url),'utf8');
const server=readFileSync(new URL('../../api/src/server.ts',import.meta.url),'utf8');
const admin=readFileSync(new URL('../src/admin-auth-backends.tsx',import.meta.url),'utf8');
test('RC330 profile font validation and default black colour',()=>{
 const preset={fontFamily:'Georgia',fontSize:28,color:'#000000',bold:true,italic:true,underline:true,strikethrough:false};
 assert.equal(validPresenterProfileFontStyle(preset),true);
 assert.equal(validPageDesign({widgets:[{id:'p',kind:'profile',profileNameStyle:preset,profileEmailStyle:{fontSize:17}}]}),true);
 for(const bad of [{fontSize:6},{fontSize:1000},{fontFamily:'javascript:'},{color:'red'},{bold:'true'},{invalid:'x'}]){
  assert.equal(validPresenterProfileFontStyle(bad),false,JSON.stringify(bad));
  assert.equal(validPageDesign({widgets:[{id:'p',kind:'profile',profileNameStyle:bad}]}),false);
 }
 assert.equal(validPageDesign({widgets:[{id:'t',kind:'text',profileEmailStyle:{fontSize:17}}]}),false);
 assert.match(ui,/presenterProfileFontCss\(profileNameStyle,22,true\)/);
 assert.match(ui,/presenterProfileFontCss\(profileEmailStyle,17,false\)/);
 assert.match(css,/\.presenter-profile-card\{[\s\S]*?color:#000000!important/);
});
test('RC330 profile photo and all texts scale with actual widget bounds',()=>{
 assert.equal(presenterProfileScale(480,190),1);
 assert.equal(presenterProfileScale(960,380),2);
 assert.equal(presenterProfileScale(240,95),.5);
 assert.equal(presenterProfileScale(480,95),.5);
 assert.equal(presenterProfileScale(0,200),1);
 assert.match(ui,/closest<HTMLElement>\('\.widget-fit-frame'\)/);
 assert.match(ui,/new ResizeObserver\(update\)/);
 assert.match(css,/\.presenter-profile-avatar\{[\s\S]*?var\(--profile-widget-scale,1\)/);
 assert.match(ui,/profileNameStyle=\{w\.profileNameStyle\} profileEmailStyle=\{w\.profileEmailStyle\}/);
 assert.match(ui,/Carattere '\+title\+' presentatore/);
});
test('RC330 custom SSO icons allow only small raster data and distinct preset badges',()=>{
 const svg='<svg xmlns="http://www.w3.org/2000/svg"></svg>';
 assert.equal(validSsoLogoData('data:image/svg+xml;base64,'+Buffer.from(svg).toString('base64')),false);
 assert.equal(validSsoLogoData('https://invalid.example/logo.png'),false);
 const png=Buffer.concat([Buffer.from([137,80,78,71,13,10,26,10,0,0,0,13]),Buffer.from('IHDR'),Buffer.alloc(20)]);
 const data='data:image/png;base64,'+png.toString('base64');
 assert.equal(validSsoLogoData(data),true);
 assert.throws(()=>validateSsoBranding('google',{logoData:data}),/invalid_sso_builtin_logo/);
 assert.doesNotThrow(()=>validateSsoBranding('infn',{logoData:data,buttonColor:'#225577'}));
 assert.throws(()=>validateSsoBranding('infn',{buttonColor:'url(https://invalid.example)'}),/invalid_sso_button_color/);
 assert.equal(publicSsoBranding('google').logoSrc,'/sso-icons/google.svg');
 assert.equal(publicSsoBranding('github').buttonColor,'#24292F');
 assert.equal(publicSsoBranding('facebook').buttonColor,'#1877F2');
 assert.equal(publicSsoBranding('infn',{logoData:'https://invalid.example/a.svg'}).logoSrc,undefined);
 assert.match(server,/publicSsoBranding\(x\.id,x\)/);
 assert.match(admin,/Carica logo custom per provider OIDC/);
 assert.match(ui,/className="sso-provider-button"/);
});
test('RC330 exact Authentik issuer and token claim preserve trailing slash',async()=>{
 const {validateDiscovery,validateClaims}=await import('../../api/src/oidc.ts');
 const provider={id:'authentik',issuer:'https://id.example/application/o/quorivio/',clientId:'client',clientSecret:'secret',redirectUri:'https://quorivio.example/api/auth/oidc/authentik/callback'};
 const disc={issuer:provider.issuer,authorization_endpoint:'https://id.example/authorize',token_endpoint:'https://id.example/token',jwks_uri:'https://id.example/jwks'};
 assert.equal(validateDiscovery(provider,disc).issuer,provider.issuer);
 assert.throws(()=>validateDiscovery({...provider,issuer:provider.issuer.slice(0,-1)},disc),/invalid_oidc_discovery/);
 const now=Math.floor(Date.now()/1000);
 const claims={iss:provider.issuer,aud:'client',sub:'alice',email:'alice@example.org',email_verified:true,nonce:'1234567890123456',exp:now+3600,iat:now};
 assert.equal(validateClaims(claims,provider,claims.nonce).subject,'alice');
 assert.throws(()=>validateClaims({...claims,iss:provider.issuer.slice(0,-1)},provider,claims.nonce),/invalid_oidc_claims/);
});
