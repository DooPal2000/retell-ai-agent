// module.exports = func => {
//     return (req, res, next) => {
//         func(req, res, next).catch(next);
//     }
// }

import { Request, Response, NextFunction } from 'express';

const catchAsync = (func: (req: Request, res: Response, next: NextFunction) => Promise<any>) => {
  return (req: Request, res: Response, next: NextFunction): void => {
    func(req, res, next).catch(next);
  };
};

export default catchAsync;
