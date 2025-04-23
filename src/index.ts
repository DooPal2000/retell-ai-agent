import express, { Request, Response, NextFunction } from 'express';
import path from 'path';
import ejsMate from 'ejs-mate';
import session from 'express-session';
import methodOverride from 'method-override';
import passport from 'passport';
import { Strategy as LocalStrategy } from 'passport-local';
import helmet from 'helmet';
import mongoSanitize from 'express-mongo-sanitize';
import flash from 'connect-flash';


// import { connectToDatabase } from './database';

import catchAsync from './utils/catchAsync';
import ExpressError from './utils/ExpressError';

// import userRoutes from './routes/user';


const app = express();

app.engine('ejs', ejsMate);
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(methodOverride('_method'));
app.use(mongoSanitize({ replaceWith: '_' }));

const sessionConfig: session.SessionOptions = {
  secret: process.env.SESSION_SECRET_KEY || 'secret',
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
    // contentSecurityPolicy: {
    //   directives: {
    //     "default-src": ["'self'"],
    //     "script-src": ["'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "'unsafe-inline'"],
    //     "style-src": ["'self'", "https://cdn.jsdelivr.net", "'unsafe-inline'"],
    //     "img-src": ["'self'", "https://images.unsplash.com", "data:"],
    //   },
    // },
  })
);

// app.use(passport.initialize());
app.use(passport.session());

// passport.use(new LocalStrategy(User.authenticate()));
// passport.serializeUser(User.serializeUser());
// passport.deserializeUser(User.deserializeUser());

app.use((req, res, next) => {
  res.locals.currentUser = req.user || null;
  res.locals.success = req.flash('success');
  res.locals.error = req.flash('error');
  next();
});

// app.use('/', userRoutes);

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

app.listen(3000, () => {
  console.log('Serving on port 3000');
});
