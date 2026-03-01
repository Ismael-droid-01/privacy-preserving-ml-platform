import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SecureTrainingComponent } from './secure-training.component';

describe('SecureTrainingComponent', () => {
  let component: SecureTrainingComponent;
  let fixture: ComponentFixture<SecureTrainingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SecureTrainingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SecureTrainingComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
