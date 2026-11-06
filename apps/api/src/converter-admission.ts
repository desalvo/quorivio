/** Separate administrator choice from deployment security prerequisites.
 * An administrator cannot bypass the container isolation policy with a switch. */
export type ConverterAdmission={deployment_enabled:boolean;worker_configured:boolean;admin_enabled:boolean;enabled:boolean;blocker:string|null};
export function converterDeploymentConfigured(env:NodeJS.ProcessEnv):boolean{
 return typeof env.QUORIVIO_CONVERTER_WORKER_URL==='string'&&/^http:\/\/[a-zA-Z0-9.-]+:\d{2,5}$/.test(env.QUORIVIO_CONVERTER_WORKER_URL)&&
 typeof env.QUORIVIO_WORKER_TOKEN==='string'&&env.QUORIVIO_WORKER_TOKEN.length>=32&&!env.QUORIVIO_WORKER_TOKEN.startsWith('REPLACE_');
}
export function converterAdmission(env:NodeJS.ProcessEnv,stored:string|null):ConverterAdmission{
 const deployment_enabled=env.QUORIVIO_ENABLE_CONVERTER==='true';
 const worker_configured=converterDeploymentConfigured(env);
 const admin_enabled=stored!=='false';
 const blocker=!deployment_enabled?'deployment_disabled':!worker_configured?'worker_configuration_missing':!admin_enabled?'disabled_by_admin':null;
 return {deployment_enabled,worker_configured,admin_enabled,enabled:blocker===null,blocker};
}
export function validConverterToggle(body:unknown):body is {enabled:boolean}{
 return !!body&&typeof body==='object'&&!Array.isArray(body)&&Object.keys(body).length===1&&typeof (body as {enabled?:unknown}).enabled==='boolean';
}
