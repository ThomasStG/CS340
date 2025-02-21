import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ItemDescriptionComponent } from './item-description.component';

describe('ItemDescriptionComponent', () => {
  let component: ItemDescriptionComponent;
  let fixture: ComponentFixture<ItemDescriptionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ItemDescriptionComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ItemDescriptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
