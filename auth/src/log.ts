export const log = {
  info: (obj: any) => console.log(JSON.stringify({ level: "info", date: new Date().toISOString(), ...obj })),
  warning: (obj: any) => console.warn(JSON.stringify({ level: "warning", date: new Date().toISOString(), ...obj })),
  error: (obj: any) => console.error(JSON.stringify({ level: "error", date: new Date().toISOString(), ...obj })),
};