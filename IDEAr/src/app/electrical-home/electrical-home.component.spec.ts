import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElectricalHomeComponent } from './electrical-home.component';

describe('ElectricalHomeComponent', () => {
  let component: ElectricalHomeComponent;
  let fixture: ComponentFixture<ElectricalHomeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ElectricalHomeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ElectricalHomeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
