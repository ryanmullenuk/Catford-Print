const data={
 booklets:[
  {label:'Finished size',name:'Size',type:'select',options:['A5','A4']},
  {label:'How many pages inc. cover?',name:'Pages',type:'select',options:['8','12','16','20','24','28','32','36','40','44','48','52','56','60']},
  {label:'How many copies?',name:'Quantity',type:'select',options:['10','25','50','100','200','300','400','500','750','1,000','1,500','2,000','2,500','3,000','4,000','5,000','6,000','8,000','10,000']},
  {label:'Customer / delivery',name:'Delivery',type:'select',options:['Account customer, 30 days credit, delivered by Parcelforce','Non account customer, payment with order, delivered by Parcelforce','Non account customer, payment with order, collected']}
 ],
 leaflets:[
  {label:'Paper',name:'Paper',type:'select',options:['130gsm','170gsm']},
  {label:'Size',name:'Size',type:'select',options:['A5','A4','A3']},
  {label:'Printed sides',name:'Sides',type:'select',options:['1 side only','Both sides']},
  {label:'Quantity',name:'Quantity',type:'select',options:['50','100','250','500','750','1,000','1,250','1,500','2,000','2,500','3,000','4,000','5,000','7,500','10,000']}
 ],
 books:[
  {label:'Book size',name:'Book size',type:'select',options:['A6 105 x 148','A5 Landscape 210 x 148','110 x 178','127 x 187','190 x 190','130 x 200','130 X 210','A5 Portrait 148 x 210','140 x 216 (5.5 x 8.5 inches)','216 x 216','178 x 229','150 x 230','156 x 234','191 x 235','170 x 244','189 x 246','154 x 254','178 x 254 (7 x 10 inches)','203 x 254','168 x 260','178 x 279','216 x 279 (8.5 x 11 inches)','210 x 280','A4 Portrait 210 x 297','A4 Landscape 297 x 210','153 x 228 (6 x 9 inches)','127 x 178 (5 x 7 inches)','US Letter 216 x 279','127 x 203 (5 x 8 inches)','Other sizes please call']},
  {label:'Quantity',name:'Quantity',type:'number',value:'100'},
  {label:'No. of pages',name:'Pages',type:'number',value:'80'},
  {label:'Cover finish',name:'Cover finish',type:'select',options:['Gloss Laminated','Matt Laminated']},
  {label:'Inner pages',name:'Inner pages',type:'select',options:['Black','Colour']},
  {label:'Paper',name:'Paper',type:'select',options:['80gsm Matt Bond','100gsm Matt Bond','120gsm Matt Bond','130gsm Gloss Art','130gsm Silk Art','85gsm Arcoprint Milk','100gsm Arcoprint Edizioni','90gsm Design Pro']},
  {label:'Delivery option',name:'Delivery',type:'select',options:['ParcelForce','Collection']},
  {label:'Bar code?',name:'Bar code',type:'select',options:['No','Yes']}
 ],
 wire:[
  {label:'Book size',name:'Book size',type:'select',options:['A4 Portrait','A4 Landscape','A5 Portrait','A5 Landscape','A3 Landscape']},
  {label:'Quantity',name:'Quantity',type:'number',value:'100'},
  {label:'No. of pages in black',name:'Black pages',type:'number',value:'80'},
  {label:'No. of pages in colour',name:'Colour pages',type:'number',value:'10'},
  {label:'No. of blank pages',name:'Blank pages',type:'number',value:'10'},
  {label:'Type of binding',name:'Binding',type:'select',options:['Wire-o Binding : White','Comb Binding : Black','Half Canadian Wire-o Binding']},
  {label:'Delivery option',name:'Delivery',type:'select',options:['ParcelForce','Collection']},
  {label:'Bar code?',name:'Bar code',type:'select',options:['No','Yes']}
 ],
 funeral:[
  {label:'Pages',name:'Pages',type:'select',options:['4 pages','8 pages','12 pages']},
  {label:'Quantity',name:'Quantity',type:'select',options:['25','35','50','75','100','150','200','250','300','350','400','500']},
  {label:'Delivery',name:'Delivery',type:'select',options:['Pickup - Free','Next working day by 6pm - £12','Next working day by noon - £18','Saturday delivery by 5pm - £24']}
 ]
};
const productNames={booklets:'Colour Booklets',leaflets:'Colour Leaflets',books:'Paperback Books',wire:'Wire Bound Books',funeral:'Funeral Order of Service'};
const productSelect=document.querySelector('#product-select');
const fields=document.querySelector('#dynamic-fields');
function renderFields(){fields.innerHTML=data[productSelect.value].map((f,i)=>{const id=`field-${i}`;const control=f.type==='select'?`<select id="${id}" data-name="${f.name}">${f.options.map(o=>`<option>${o}</option>`).join('')}</select>`:`<input id="${id}" data-name="${f.name}" type="number" min="1" value="${f.value}">`;return `<label for="${id}">${f.label}${control}</label>`}).join('')}
productSelect.addEventListener('change',renderFields);renderFields();
document.querySelectorAll('[data-product]').forEach(a=>a.addEventListener('click',()=>{productSelect.value=a.dataset.product;renderFields()}));
document.querySelector('#quote-form').addEventListener('submit',e=>{e.preventDefault();const lines=[`Product: ${productNames[productSelect.value]}`];fields.querySelectorAll('select,input').forEach(el=>lines.push(`${el.dataset.name}: ${el.value}`));const notes=document.querySelector('#notes').value.trim();if(notes)lines.push(`Notes: ${notes}`);location.href=`mailto:web@catfordprint.co.uk?subject=${encodeURIComponent(productNames[productSelect.value]+' quotation')}&body=${encodeURIComponent('Please provide a firm quotation for the following:\n\n'+lines.join('\n'))}`});
const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('.main-nav');menu.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')==='true';menu.setAttribute('aria-expanded',String(!open));nav.classList.toggle('open')});
const productsButton=document.querySelector('.has-menu>button'),navItem=document.querySelector('.has-menu');productsButton.addEventListener('click',()=>{const open=productsButton.getAttribute('aria-expanded')==='true';productsButton.setAttribute('aria-expanded',String(!open));navItem.classList.toggle('open')});
document.addEventListener('click',e=>{if(!navItem.contains(e.target)){navItem.classList.remove('open');productsButton.setAttribute('aria-expanded','false')}});
document.querySelector('#year').textContent=new Date().getFullYear();
