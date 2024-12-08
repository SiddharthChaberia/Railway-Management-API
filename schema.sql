use railway_management;

drop table if exists users;
create table users (
	user_id int auto_increment PRIMARY KEY,
    first_name varchar(50) NOT NULL,
    last_name varchar(50),
    phone int NOT NULL,
    email varchar(100) NOT NULL,
    pwd varchar(100) NOT NULL,
    role enum('admin','customer') NOT NULL
);

drop table if exists trains;
create table trains (
	train_id int auto_increment PRIMARY KEY,
    train_name varchar(200) NOT NULL,
    source_stop varchar(200) NOT NULL,
    dest_stop varchar(200) NOT NULL,
    seat_avl int NOT NULL
);

drop table if exists bookings;
create table bookings (
	id int auto_increment PRIMARY KEY,
    user_id int,
    train_id int,
    book_time timestamp default current_timestamp,
    seats_booked int NOT NULL,
    status enum('confirmed') DEFAULT 'confirmed',
    foreign key (user_id) references users(user_id),
    foreign key (train_id) references trains(train_id)
); 