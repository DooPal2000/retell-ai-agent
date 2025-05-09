import mongoose, { Schema, Document, Model } from 'mongoose';
import passportLocalMongoose from 'passport-local-mongoose';

export interface IUser extends Document {
    username: string;
    role: 'user' | 'admin';
    createdAt: Date;
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

const User = mongoose.model<IUser>('User', userSchema);

export default User;
