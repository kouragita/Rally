class Logger {
  log(message: string, ...args: any[]) {
    console.log(`[RallyApp] ${message}`, ...args);
  }

  error(message: string, ...args: any[]) {
    console.error(`[RallyApp] ERROR: ${message}`, ...args);
  }

  warn(message: string, ...args: any[]) {
    console.warn(`[RallyApp] WARN: ${message}`, ...args);
  }

  info(message: string, ...args: any[]) {
    console.info(`[RallyApp] INFO: ${message}`, ...args);
  }
}

export const logger = new Logger();
