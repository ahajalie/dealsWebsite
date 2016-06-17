Create Table Product (
	id MEDIUMINT PRIMARY KEY AUTO_INCREMENT, 
	normalPrice DECIMAL(6,2),
	promoPrice DECIMAL(6,2),
	productTitle VARCHAR(100),
	sellerEmail VARCHAR(100),
	category VARCHAR(100),
	sellerID VARCHAR(40),
	sellerAccountName VARCHAR(100),
	brand VARCHAR(40),
	imageURL VARCHAR(300),
	startDate DATE
);

Create Table User (
	id MEDIUMINT PRIMARY KEY AUTO_INCREMENT,
	email VARCHAR(100),
	salt VARCHAR(8),
	pass VARCHAR(40),
	token VARCHAR(40),
	tokenIssueDate TIMESTAMP DEFAULT 0
	);

Create Table Codes (
	product_id MEDIUMINT,
	user_id MEDIUMINT,
	productCode VARCHAR(40),
	dateIssued TIMESTAMP DEFAULT 0,
	FOREIGN KEY (product_id) REFERENCES Product(id),
	FOREIGN KEY (user_id) REFERENCES User(id),
	UNIQUE (productCode)
);