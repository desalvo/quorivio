/** Type-only fallback for offline development; production resolves ldapts 9.x. */
declare module 'ldapts' {
 export class Client {
  constructor(options:{url:string;timeout?:number;connectTimeout?:number;tlsOptions?:object});
  startTLS(options:object):Promise<void>;
  bind(dn:string,password:string):Promise<void>;
  search(baseDn:string,options:{scope:string;filter:string;attributes:string[];sizeLimit:number;timeLimit:number}):Promise<{searchEntries:Record<string,unknown>[]}>;
  unbind():Promise<void>;
 }
}
