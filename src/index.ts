import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import ejsMate from 'ejs-mate';
import session from 'express-session';
import methodOverride from 'method-override';
import passport from 'passport';
import { Strategy as LocalStrategy } from 'passport-local';
import helmet from 'helmet';

import flash from 'connect-flash';
import User, { IUser } from './models/user';
import mongoSanitize from 'express-mongo-sanitize';
import { connectToDatabase } from './database';
import config from './config';


import catchAsync from './utils/catchAsync';
import ExpressError from './utils/ExpressError';

import userRoutes from './routes/user';


const app = express();

app.engine('ejs', ejsMate);
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(methodOverride('_method'));



// // sanitizeMongoInput 함수 정의 (입력값 검증)
// function sanitizeMongoInput(input: any): any {
//   if (typeof input === 'string') {
//     return input.replace(/[.*$&^%]/g, '');  // 특수 문자 제거
//   }
//   return input;
// }

// // 미들웨어에서 req.query와 req.body 필터링
// app.use((req: Request, res: Response, next: NextFunction) => {
//   // req.query 타입 명시: query가 key-value 객체임을 명시
//   const sanitizedQuery: { [key: string]: any } = {};
  
//   for (let key in req.query) {
//     sanitizedQuery[key] = sanitizeMongoInput(req.query[key]);
//   }
//   // 새 객체를 사용해 req.query를 덮어씌우는 대신, req.query에 직접 할당
//   req.query = { ...sanitizedQuery };  

//   // req.body 타입을 명확히 설정
//   if (req.body) {
//     const sanitizedBody: { [key: string]: any } = {};
//     for (let key in req.body) {
//       sanitizedBody[key] = sanitizeMongoInput(req.body[key]);
//     }
//     req.body = { ...sanitizedBody};
//   }

//   next();
// });



const sessionConfig: session.SessionOptions = {
  secret: config.session.secretKey,
  resave: false,
  saveUninitialized: true,
  cookie: {
    httpOnly: true,
    expires: new Date(Date.now() + 1000 * 60 * 60 * 24 * 3),
    maxAge: 1000 * 60 * 60 * 24 * 3,
  },
};

app.use(session(sessionConfig));
app.use(flash());

app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        "default-src": ["'self'"],
        "script-src": ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "'unsafe-inline'"],
        "style-src": ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
        "img-src": ["'self'", "https://images.unsplash.com", "data:"],
      },
    },
  })
);

app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser() as any);
passport.deserializeUser(User.deserializeUser() as any);

app.use((req, res, next) => {
  console.log('User:', req.user);
  console.log('Is Authenticated:', req.isAuthenticated());

  res.locals.currentUser = req.user || null;
  res.locals.success = req.flash('success');
  res.locals.error = req.flash('error');
  next();
});


app.use('/', userRoutes);

app.get('/', (req, res) => {
  res.render('home');
});

app.all('/{*any}', (req, res, next) => {
  next(new ExpressError('Page Not Found', 404));
});

app.use((err: any, req: Request, res: Response, next: NextFunction) => {
  const { statusCode = 500 } = err;
  if (!err.message) err.message = 'Oh No, Something Went Wrong!';
  res.status(statusCode).render('error', { err });
});

// 데이터베이스 연결
connectToDatabase().catch(console.error);

app.listen(3000, () => {
  console.log('Serving on port 3000');
});