// class ExpressError extends Error {
//     constructor(message, statusCode) {
//         super();
//         this.message = message;
//         this.statusCode = statusCode;
//     }
// }

// module.exports = ExpressError;

// src/utils/ExpressError.ts

export default class ExpressError extends Error {
    statusCode: number;
  
    constructor(message: string, statusCode: number) {
      super(message);
      this.statusCode = statusCode;
  
      // Set the prototype explicitly (필수 아님, 일부 환경에서 상속 문제 방지용)
      Object.setPrototypeOf(this, ExpressError.prototype);
    }
  }
  