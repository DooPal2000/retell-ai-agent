import { Request, Response, NextFunction } from 'express';
// import Product from '../models/product';
import User, { IUser } from '../models/user';
import ExpressError from '../utils/ExpressError';
import passport from 'passport';

export const renderRegister = (req: Request, res: Response) => {
    res.render('users/register');
};

export const renderRegisterAdmin = (req: Request, res: Response) => {
    res.render('users/registerAdmin');
};

export const register = async (req: Request, res: Response) => {
    const { username, password } = req.body;
    const user = new User({
        username
    });
    const registerUser = await User.register(user, password);
    res.redirect('/');
};

export const registerAdmin = async (req: Request, res: Response, next: NextFunction) => {
    const { username, password } = req.body;

    const user = new User({
        username,
        role: 'admin'
    });

    const registerUser = await User.register(user, password);
    req.login(registerUser, err => {
        if (err) return next(err);
        res.redirect('/admin-dashboard');
    });
};

export const renderLogin = (req: Request, res: Response) => {
    res.render('users/login');
};

export const login = (req: Request, res: Response, next: NextFunction) => {
    passport.authenticate('local', (err: Error, user: any, info: any) => {
        if (err) {
            return next(err);
        }
        if (!user) {
            req.flash('error', info.message || '로그인 실패');
            return res.redirect('/login');
        }
        req.logIn(user, (err) => {
            if (err) {
                return next(err);
            }
            if (user.role === 'admin') {
                return res.redirect('/admin');
            } else {
                return res.redirect('/products');
            }
        });
    })(req, res, next);
};

export const logout = (req: Request, res: Response, next: NextFunction) => {
    req.logout(function (err) {
        if (err) {
            return next(err);
        }
        res.redirect('/');
    });
};

// export const renderProduct = async (req: Request, res: Response) => {
//     const currentUser = req.user;
//     const products = await Product.find({ createdBy: currentUser._id });
//     res.render('products/product', { products: products });
// };
