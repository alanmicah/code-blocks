const originalString = `
<span style="font-family:Arial; font-size: 13px;">1 x Novoferm Steel Made to Measure Georgian up &amp; over Retractable Garage Door finished in White  1 2638.00 25% Sales 20% (VAT on Income) 1978.50<br />
1 1 x Steel Frame finished in White 1 270.00 25% Sales 20% (VAT on Income) 202.50<br />
4 UPVC finishing trim in white 1 75.00 Sales - UPVC 20% (VAT on Income) 75.00<br />
6 Removal &amp; Disposal of existing garage door 1 30.00 Sales - Disposal 20% (VAT on Income) 30.00<br />
5 Installation 1 330.00 Sales 20% (VAT on Income) 330.00<br />
<br />
Total VAT 20.00%523.20<br />
TotalGBP &pound;3,139.20<br />
<br />
Optional Extras for Novoferm 1 x Novomatic 563 motor (c/w 2 remotes &amp; 1 internal wall unit): &pound;429+VAT 1 x Rubber Hump (fitted to the ground where the door will sit, helps prevent water from entering the garage): &pound;149+VAT 1 x Brush strip (prevent and debris from entering under the door): &pound;125+VAT</span>
`;

let strippedString = originalString.replace(/(<([^>]+)>)/gi, "");
strippedString = strippedString.replace(/&pound;/gi, "£");
strippedString = strippedString.replace(/&amp;/gi, "&");

console.log(strippedString);
