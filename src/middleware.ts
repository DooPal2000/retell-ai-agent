// middlewares/auth.ts

import { Request, Response, NextFunction } from 'express';
// import { user } from './models/user';  // IUser 인터페이스는 user 모델에 정의되어 있어야 함
import ExpressError from './utils/ExpressError';

// 아래에서 `AuthenticatedRequest`를 사용하지 않음
export const isLoggedIn = (req: Request, res: Response, next: NextFunction): void => {
    console.log("Req.user...", req.user);
    if (!req.isAuthenticated()) {
        // req.session.returnTo = req.originalUrl;
        req.flash('error', '로그인 해 주세요.');
        return res.redirect('/login');
    }
    next();
};

export const isAuthorized = (req: Request, res: Response, next: NextFunction): void => {
    if (!req.isAuthenticated()) {
        req.flash('error', '활성화된 고객님이 아닙니다. 관리자에게 문의해 주세요.');
        return res.redirect('/login');
    }
    next();
};

export const isAdmin = (req: Request, res: Response, next: NextFunction): void => {
    if (!req.isAuthenticated() || req.user?.role !== 'admin') {
        req.flash('error', '관리자가 아닙니다.');
        return res.redirect('/login');
    }
    next();
};

export const isSecureAdminCreation = (req: Request, res: Response, next: NextFunction): void => {
    const userPhoneNumber = req.body.phonenum;
    const adminNumbers = JSON.parse(process.env.ADMIN_NUMBERS || '[]');

    if (!Object.values(adminNumbers).includes(userPhoneNumber)) {
        req.flash('error', '관리자 계정 생성이 불가합니다.');
        return res.redirect('/unauthorized');
    }
    next();
};
