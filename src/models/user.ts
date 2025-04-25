import mongoose, { Document, Schema } from 'mongoose';
import passportLocalMongoose from 'passport-local-mongoose';

interface IUser extends Document {
    role: 'user' | 'admin';
    createdAt: Date;
}

interface IUserModel extends mongoose.Model<IUser> {
    authenticate(): any;
    serializeUser(): any;
    deserializeUser(): any;
}

const userSchema = new Schema({
    role: {
        type: String,
        enum: ['user', 'admin'],
        default: 'user'
    },
    createdAt: {
        type: Date,
        default: Date.now
    }
});

userSchema.plugin(passportLocalMongoose);

const User = mongoose.model<IUser, IUserModel>("User", userSchema);

export default User;
