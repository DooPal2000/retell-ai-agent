import mongoose, { Schema, Document } from 'mongoose';
import passportLocalMongoose from 'passport-local-mongoose';

export interface IUser extends Document {
    username: string;
    role: 'user' | 'admin';
    createdAt: Date;
}

interface IUserModel extends mongoose.Model<IUser> {
    authenticate(): any;
    serializeUser(): any;
    deserializeUser(): any;
    register(user: IUser, password: string): Promise<IUser>;
}

const userSchema = new Schema({
    username: {
        type: String,
        required: true,
        unique: true
    },
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

const User = mongoose.model<IUser, IUserModel>('User', userSchema);

export default User;
